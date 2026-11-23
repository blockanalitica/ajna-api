import logging
from contextlib import suppress
from time import perf_counter

from django.http import HttpResponse
from django.urls import Resolver404, resolve
from django.utils.deprecation import MiddlewareMixin

from ajna import metrics

log = logging.getLogger(__name__)

_HTTP_METHODS = {"CONNECT", "DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT", "TRACE"}


class HealthCheckMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.META["PATH_INFO"] == "/ping/":
            return HttpResponse("pong!")


class RequestMetricsMiddleware:
    sync_capable = True
    async_capable = False

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        started_at = perf_counter()
        try:
            response = self.get_response(request)
        except Exception:
            self.record(request, 500, perf_counter() - started_at)
            raise

        self.record(request, response.status_code, perf_counter() - started_at)
        return response

    def record(self, request, status_code, duration):
        try:
            attributes = {
                "http.request.method": request.method
                if request.method in _HTTP_METHODS
                else "_OTHER",
                "http.response.status_code": status_code,
                "url.scheme": request.scheme,
            }
            route = self._route(request)
            if route is not None:
                attributes["http.route"] = route
            if status_code >= 500:
                attributes["error.type"] = str(status_code)
            metrics.record_request(duration, attributes)
        except Exception:
            log.exception("Unable to record request metrics")

    @staticmethod
    def _route(request):
        resolver_match = getattr(request, "resolver_match", None)
        if resolver_match is None:
            with suppress(Resolver404):
                resolver_match = resolve(
                    request.path_info, urlconf=getattr(request, "urlconf", None)
                )
        if resolver_match is not None:
            return resolver_match.route or resolver_match.view_name
        if request.path_info == "/ping/":
            return "/ping/"
        return None
