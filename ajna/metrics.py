import gc
import logging
import os
from functools import cache
from threading import Lock
from uuid import uuid4

from django.conf import settings
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.metrics import NoOpMeterProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource

log = logging.getLogger(__name__)
_provider = None
_provider_pid = None
_lock = Lock()
_noop_meter = NoOpMeterProvider().get_meter("ajna.metrics")
_DURATION_BUCKETS = (
    0.001,
    0.005,
    0.01,
    0.025,
    0.05,
    0.1,
    0.25,
    0.5,
    1,
    2.5,
    5,
    10,
    30,
    60,
    120,
    300,
    600,
)


def _prepare_fork():
    global _provider, _provider_pid
    _lock.acquire()
    try:
        shutdown()
    finally:
        _provider = None
        _provider_pid = None
        _instrument.cache_clear()
        gc.collect()


def _resume_after_fork():
    _lock.release()


def _reset_after_fork():
    global _lock
    _lock = Lock()


os.register_at_fork(
    before=_prepare_fork,
    after_in_parent=_resume_after_fork,
    after_in_child=_reset_after_fork,
)


def get_meter():
    if not settings.OTLP_METRICS_ENDPOINT:
        return _noop_meter

    global _provider, _provider_pid
    pid = os.getpid()
    with _lock:
        if _provider is None or _provider_pid != pid:
            exporter = OTLPMetricExporter(endpoint=settings.OTLP_METRICS_ENDPOINT)
            reader = PeriodicExportingMetricReader(exporter)
            _provider = MeterProvider(
                metric_readers=[reader],
                resource=Resource.create(
                    {
                        "service.name": settings.OTLP_SERVICE_NAME,
                        "service.instance.id": str(uuid4()),
                    }
                ),
            )
            _provider_pid = pid
        return _provider.get_meter("ajna.metrics")


@cache
def _instrument(meter, kind, name, unit):
    create = getattr(meter, f"create_{kind}")
    if kind == "histogram" and unit == "s":
        return create(name, unit=unit, explicit_bucket_boundaries_advisory=_DURATION_BUCKETS)
    return create(name, unit=unit)


def _record(kind, name, value, unit="1", attributes=None):
    try:
        instrument = _instrument(get_meter(), kind, str(name), unit)
        if kind == "gauge":
            instrument.set(value, attributes)
        elif kind == "histogram":
            instrument.record(value, attributes)
        else:
            instrument.add(value, attributes)
    except Exception:
        log.exception("Unable to record metric %s", name)


def record_duration(name, seconds, attributes=None):
    _record("histogram", name, seconds, unit="s", attributes=attributes)


def raw_timer(key, value):
    if isinstance(value, int | float):
        record_duration(key, value / 1000)


def increment(key, delta=1, subname=None, *, prefix="counters."):
    name = f"{prefix}{key}"
    if subname:
        name += f".{subname}"
    _record("up_down_counter", name, delta)


def gauge(key, value=1, subname=None):
    name = f"{key}.{subname}" if subname else key
    _record("gauge", name, value)


def record_request(duration, attributes):
    _record("counter", "http.server.requests", 1, attributes=attributes)
    record_duration("http.server.request.duration", duration, attributes)


def shutdown():
    if _provider is not None and _provider_pid == os.getpid():
        _provider.shutdown()
