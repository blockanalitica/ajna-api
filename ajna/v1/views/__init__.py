import importlib
import logging
from datetime import datetime, timedelta

from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from ajna.utils.views import PaginatedApiView, RawSQLPaginatedApiView

log = logging.getLogger(__name__)


class ModelMapping:
    def __init__(self, version, network, **kwargs):
        module_path = ".".join([version.lower(), network.lower()])
        module = importlib.import_module("ajna.{}.chain".format(module_path))
        if hasattr(module, "MODEL_MAP"):
            for key, model in module.MODEL_MAP.items():
                setattr(self, key, model)


class DaysAgoMixin:
    days_ago = None
    days_ago_default = None
    days_ago_required = False
    days_ago_options = []
    days_ago_dt = None

    def _handle_days_ago(self, request):
        days_ago = request.GET.get("days_ago", self.days_ago_default)
        if days_ago:
            try:
                self.days_ago = int(days_ago)
                self.days_ago_dt = datetime.now() - timedelta(days=self.days_ago)
            except (TypeError, ValueError):
                raise ValidationError("Wrong value for days_ago")

            if self.days_ago_options and self.days_ago not in self.days_ago_options:
                raise ValidationError("Wrong value for days_ago")

        elif self.days_ago_required:
            raise ValidationError("days_ago is a required param")


class BaseChainMixin:
    def dispatch(self, request, *args, **kwargs):
        path_parts = request.path.lstrip("/").rstrip("/").split("/")
        self.protocol_version, self.protocol_network = path_parts[:2]

        self._handle_days_ago(request)

        self.models = ModelMapping(self.protocol_version, self.protocol_network)

        return super().dispatch(request, *args, **kwargs)


class BaseChainView(DaysAgoMixin, BaseChainMixin, APIView):
    pass


class PaginatedChainView(DaysAgoMixin, BaseChainMixin, PaginatedApiView):
    pass


class RawSQLPaginatedChainView(DaysAgoMixin, BaseChainMixin, RawSQLPaginatedApiView):
    pass
