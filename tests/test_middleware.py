import pytest
from django.http import HttpResponse
from django.test import RequestFactory
from django.urls import path

from ajna.middleware import RequestMetricsMiddleware


@pytest.fixture
def record(mocker):
    return mocker.patch("ajna.metrics.record_request")


def test_routes_group_dynamic_values(record):
    urlconf = (path("pools/<pool_address>/", lambda _: HttpResponse()),)
    for address in ("0x123", "0x456"):
        request = RequestFactory().get(f"/pools/{address}/")
        request.urlconf = urlconf
        RequestMetricsMiddleware(lambda _: HttpResponse())(request)

    assert record.call_count == 2
    for call in record.call_args_list:
        assert call.args[0] >= 0
        assert call.args[1] == {
            "http.request.method": "GET",
            "http.response.status_code": 200,
            "url.scheme": "http",
            "http.route": "pools/<pool_address>/",
        }


def test_unknown_urls_and_methods_are_bounded(record):
    request = RequestFactory().generic("ARBITRARY", "/unknown/secret/")

    RequestMetricsMiddleware(lambda _: HttpResponse(status=404))(request)

    assert record.call_args.args[1] == {
        "http.request.method": "_OTHER",
        "http.response.status_code": 404,
        "url.scheme": "http",
    }


def test_exception_is_recorded_and_propagated(record, mocker):
    handler = mocker.Mock(side_effect=ValueError("failed view"))

    with pytest.raises(ValueError, match="failed view"):
        RequestMetricsMiddleware(handler)(RequestFactory().get("/unknown/"))

    assert record.call_args.args[1]["http.response.status_code"] == 500
    assert record.call_args.args[1]["error.type"] == "500"


def test_ping_is_recorded_through_configured_stack(client, record):
    response = client.get("/ping/")

    assert response.content == b"pong!"
    assert record.call_args.args[1]["http.route"] == "/ping/"


def test_recording_failure_does_not_fail_request(mocker):
    mocker.patch("ajna.metrics.record_request", side_effect=RuntimeError("export failed"))

    response = RequestMetricsMiddleware(lambda _: HttpResponse())(RequestFactory().get("/ping/"))

    assert response.status_code == 200
