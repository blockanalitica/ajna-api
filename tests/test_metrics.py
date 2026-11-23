import json
import os
import threading
import time

import pytest
from opentelemetry.proto.collector.metrics.v1.metrics_service_pb2 import (
    ExportMetricsServiceRequest,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    InMemoryMetricReader,
    MetricExporter,
    MetricExportResult,
)

from ajna import celery_app, metrics

ENDPOINT = "https://metrics.example/opentelemetry/v1/metrics"


@pytest.fixture
def metric_reader(mocker):
    reader = InMemoryMetricReader()
    provider = MeterProvider(metric_readers=[reader])
    mocker.patch.object(metrics, "get_meter", return_value=provider.get_meter("ajna.metrics"))
    yield reader
    provider.shutdown()
    metrics._instrument.cache_clear()


@pytest.fixture
def fresh_provider(mocker):
    mocker.patch.object(metrics, "_provider", None)
    mocker.patch.object(metrics, "_provider_pid", None)
    yield
    metrics.shutdown()
    metrics._instrument.cache_clear()


def collected(reader):
    return {
        metric.name: metric
        for resource in reader.get_metrics_data().resource_metrics
        for scope in resource.scope_metrics
        for metric in scope.metrics
    }


def test_metrics_export_values_and_units(metric_reader):
    metrics.raw_timer("celery.task.run", 1500)
    metrics.increment("users", 3, "active")
    metrics.increment("users", -1, "active")
    metrics.gauge("queue", -2, "size")
    metrics.gauge("queue", -3, "size")

    values = collected(metric_reader)
    assert values["celery.task.run"].unit == "s"
    assert values["celery.task.run"].data.data_points[0].sum == 1.5
    assert values["counters.users.active"].data.data_points[0].value == 2
    assert values["queue.size"].data.data_points[0].value == -3


def test_raw_timer_ignores_non_numeric_values(metric_reader):
    metrics.raw_timer("celery.task.run", "1500")

    assert metric_reader.get_metrics_data() is None


def test_metrics_failure_is_swallowed(mocker):
    mocker.patch.object(metrics, "get_meter", side_effect=RuntimeError("exporter unavailable"))

    metrics.increment("failed")


def test_disabled_endpoint_does_not_initialize_exporter(settings, mocker):
    settings.OTLP_METRICS_ENDPOINT = ""
    exporter = mocker.patch.object(metrics, "OTLPMetricExporter")

    metrics.increment("disabled")

    exporter.assert_not_called()


@pytest.mark.usefixtures("fresh_provider")
def test_provider_config_and_process_isolation(settings, mocker):
    settings.OTLP_METRICS_ENDPOINT = ENDPOINT
    settings.OTLP_SERVICE_NAME = "ajna-test"
    exporter = mocker.patch.object(metrics, "OTLPMetricExporter")
    reader = mocker.patch.object(metrics, "PeriodicExportingMetricReader")
    provider = mocker.patch.object(metrics, "MeterProvider")

    metrics.get_meter()
    metrics.get_meter()

    exporter.assert_called_once_with(endpoint=ENDPOINT)
    reader.assert_called_once_with(exporter.return_value)
    assert provider.call_count == 1
    resource = provider.call_args.kwargs["resource"]
    assert resource.attributes["service.name"] == "ajna-test"
    first_instance = resource.attributes["service.instance.id"]

    mocker.patch.object(metrics.os, "getpid", return_value=os.getpid() + 1)
    metrics.get_meter()

    assert provider.call_count == 2
    assert provider.call_args.kwargs["resource"].attributes["service.instance.id"] != first_instance
    metrics.shutdown()
    provider.return_value.shutdown.assert_called_once()


def test_celery_metrics_use_otlp(metric_reader, mocker):
    mocker.patch.object(celery_app.time, "perf_counter", side_effect=[10, 11.5])

    celery_app._start_timer("run", "celery.example", "task-id")
    celery_app._stop_timer("run", "celery.example", "task-id")
    celery_app.metrics_task_success("example")
    celery_app.metrics_task_failure("example")
    celery_app.metrics_task_retry("example")
    celery_app.metrics_task_revoked("example")

    values = collected(metric_reader)
    assert values["celery.example.run"].data.data_points[0].sum == 1.5
    for event in ("success", "failure", "retry", "revoked"):
        assert values[f"celery.example.{event}"].data.data_points[0].value == 1


def test_otlp_http_payload(settings, mocker, responses, fresh_provider):
    settings.OTLP_METRICS_ENDPOINT = ENDPOINT
    settings.OTLP_SERVICE_NAME = "ajna-test"
    mocker.patch.dict(os.environ, {"OTEL_METRIC_EXPORT_INTERVAL": "3600000"})
    responses.add(responses.POST, ENDPOINT, body=b"", status=200)

    try:
        metrics.increment("task.success")
        metrics.gauge("queue.size", 5)
        metrics.raw_timer("task.run", 1250)
        metrics.record_request(
            0.25, {"http.route": "pools/<pool_address>/", "http.response.status_code": 200}
        )

        assert metrics._provider.force_flush()
        request = responses.calls[0].request
        assert request.headers["Content-Type"] == "application/x-protobuf"
        payload = ExportMetricsServiceRequest.FromString(request.body)
        resource = payload.resource_metrics[0]
        attributes = {item.key: item.value.string_value for item in resource.resource.attributes}
        assert attributes["service.name"] == "ajna-test"
        assert attributes["service.instance.id"]
        values = {item.name: item for scope in resource.scope_metrics for item in scope.metrics}
        assert values["counters.task.success"].sum.data_points[0].as_int == 1
        assert values["queue.size"].gauge.data_points[0].as_int == 5
        assert values["task.run"].histogram.data_points[0].sum == 1.25
        assert values["http.server.requests"].sum.data_points[0].as_int == 1
        assert values["http.server.request.duration"].histogram.data_points[0].sum == 0.25
    finally:
        metrics.shutdown()


class NullExporter(MetricExporter):
    def export(self, metrics_data, timeout_millis=10000, **kwargs):
        return MetricExportResult.SUCCESS

    def force_flush(self, timeout_millis=10000):
        return True

    def shutdown(self, timeout_millis=30000, **kwargs):
        pass


@pytest.mark.usefixtures("fresh_provider")
def test_fork_does_not_inherit_export_threads(settings, mocker):
    settings.OTLP_METRICS_ENDPOINT = ENDPOINT
    mocker.patch.object(metrics, "OTLPMetricExporter", side_effect=lambda **kwargs: NullExporter())
    metrics.increment("parent")
    parent_instance = metrics._provider._sdk_config.resource.attributes["service.instance.id"]

    read_fd, write_fd = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(read_fd)
        try:
            time.sleep(0.05)
            inherited_threads = sum(
                thread.name == "OtelPeriodicExportingMetricReader"
                for thread in threading.enumerate()
            )
            metrics.increment("child")
            child_instance = metrics._provider._sdk_config.resource.attributes[
                "service.instance.id"
            ]
            metrics.shutdown()
            os.write(write_fd, json.dumps([inherited_threads, child_instance]).encode())
        finally:
            os.close(write_fd)
            os._exit(0)

    os.close(write_fd)
    try:
        inherited_threads, child_instance = json.loads(os.read(read_fd, 4096))
        assert inherited_threads == 0
        assert child_instance != parent_instance
        assert metrics._provider is None
        metrics.increment("parent.after_fork")
        assert (
            metrics._provider._sdk_config.resource.attributes["service.instance.id"]
            != child_instance
        )
    finally:
        os.close(read_fd)
        os.waitpid(pid, 0)
