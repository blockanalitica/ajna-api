import importlib
import logging
from datetime import datetime, timedelta

from django.http import Http404
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from ajna.constants import AJNA_DEPLOYMENTS
from ajna.utils.views import PaginatedApiView, RawSQLPaginatedApiView

log = logging.getLogger(__name__)


def _get_module(version, network):
    module_path = ".".join([version.lower(), network.lower()])
    module = importlib.import_module("ajna.{}.chain".format(module_path))
    return module


def _get_path_parts(request):
    version, network = request.path.lstrip("/").rstrip("/").split("/")[:2]
    if (
        version not in AJNA_DEPLOYMENTS["versions"]
        or network not in AJNA_DEPLOYMENTS["networks"]
    ):
        raise Http404("Invalid path")
    return version, network


class ModelMapping:
    def __init__(self, version, network, **kwargs):
        module = _get_module(version, network)
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
    _chain = None

    @property
    def chain(self):
        if not self._chain:
            module = _get_module(self.protocol_version, self.protocol_network)
            cls_name = "{}".format(
                self.protocol_version.capitalize(), self.protocol_network.capitalize()
            )
            cls = getattr(module, cls_name)
            self._chain = cls()
        return self._chain

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.protocol_version, self.protocol_network = _get_path_parts(request)

        self._handle_days_ago(request)

        self.models = ModelMapping(self.protocol_version, self.protocol_network)


class BaseChainView(DaysAgoMixin, BaseChainMixin, APIView):
    pass


class PaginatedChainView(DaysAgoMixin, BaseChainMixin, PaginatedApiView):
    pass


class RawSQLPaginatedChainView(DaysAgoMixin, BaseChainMixin, RawSQLPaginatedApiView):
    pass
