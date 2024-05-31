import importlib
import logging
from datetime import datetime, timedelta

from django.core.paginator import InvalidPage
from django.core.paginator import Paginator as DefaultPaginator
from django.db import connection
from django.http import Http404
from django.utils.functional import cached_property
from psycopg2.sql import SQL, Composable, Identifier, Literal
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from ajna.constants import AJNA_DEPLOYMENTS
from ajna.utils.db import fetch_all

log = logging.getLogger(__name__)


class RawQuerySetPaginator(DefaultPaginator):
    def __init__(self, sql, count_query, per_page, orphans=0, allow_empty_first_page=True):
        self.raw_sql, self.sql_vars = sql
        self.count_sql, self.count_sql_vars = count_query
        super().__init__(
            None,
            per_page,
            orphans=orphans,
            allow_empty_first_page=allow_empty_first_page,
        )

    def _get_limit_offset_query(self, limit, offset):
        return SQL("{} LIMIT {} OFFSET {}").format(
            self.raw_sql,
            Literal(limit),
            Literal(offset),
        )

    def page(self, number):
        """Return a Page object for the given 1-based page number."""
        number = self.validate_number(number)
        offset = (number - 1) * self.per_page
        limit = self.per_page
        if offset + limit + self.orphans >= self.count:
            limit = self.count - offset

        query_with_limit = self._get_limit_offset_query(limit, offset)

        results = fetch_all(query_with_limit, self.sql_vars)

        return self._get_page(results, number, self)

    @cached_property
    def count(self):
        if self.count_sql:
            count_query = self.count_sql
            count_sql_vars = self.count_sql_vars
        else:
            count_query = SQL("SELECT COUNT(*) FROM ({}) AS count_sub_query").format(self.raw_sql)
            count_sql_vars = self.sql_vars

        with connection.cursor() as cursor:
            cursor.execute(count_query, count_sql_vars)
            count = cursor.fetchone()[0]

        return count

    def _check_object_list_is_ordered(self):
        pass


class RawPagination(PageNumberPagination):
    django_paginator_class = RawQuerySetPaginator
    page_size = 20
    page_size_query_param = "p_size"
    max_page_size = 100
    page_query_param = "p"

    def get_paginated_response(self, results, additional_data):
        response_data = {
            "count": self.page.paginator.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": results,
        }
        response_data.update(additional_data)
        return Response(response_data)

    def paginate_queryset(self, queryset, count_query, request, view=None):
        self.request = request
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, count_query, page_size)
        page_number = self.get_page_number(request, paginator)

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(page_number=page_number, message=str(exc))
            raise NotFound(msg) from None

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        return list(self.page)


class InvalidMethod(AttributeError):
    pass


class RawSQLPaginatedApiView(APIView):
    ordering_fields = []
    search_fields = []
    default_order = None
    serializer_class = None
    model = None
    lookup_field = None
    queryset_extra = None
    order_nulls_last = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.paginator = RawPagination()

    def get_queryset(self, **kwargs):
        raise InvalidMethod(
            "RawSQLPaginatedApiView needs get_raw_sql to be implemented instead of " "get_queryset"
        )

    def get_count_sql(self, **kwargs):
        return None, None

    def get_raw_sql(self, **kwargs):
        """
        Returns a raw_sql with vars to be passed to execute
        """
        raise NotImplementedError

    def get_search_filters(self, request):
        search = request.query_params.get("search")
        filters = []
        if search and self.search_fields:
            for field in self.search_fields:
                filters.append("{} ilike %s ESCAPE ''".format(field))

            search = "%{}%".format(search)
            return "({})".format(" OR ".join(filters)), [search] * len(self.search_fields)
        return None

    def get_ordering(self, request):
        param = request.query_params.get("order")
        ordering_fields = []
        for field in self.ordering_fields:
            ordering_fields.append(field)
            ordering_fields.append("-{}".format(field))

        if param in ordering_fields:
            return param
        return self.default_order

    def paginate_queryset(self, queryset, count_query):
        return self.paginator.paginate_queryset(queryset, count_query, self.request, view=self)

    def get_additional_data(self, data, **kwargs):
        return {}

    def get(self, request, **kwargs):
        search_filters = self.get_search_filters(request)
        raw_sql, sql_vars = self.get_raw_sql(
            search_filters=search_filters, query_params=request.GET, **kwargs
        )
        if not isinstance(raw_sql, Composable):
            raw_sql = SQL(raw_sql)

        if sql_vars and not isinstance(sql_vars, (list, dict)):
            raise TypeError

        count_sql, count_sql_vars = self.get_count_sql(
            search_filters=search_filters, query_params=request.GET, **kwargs
        )
        if count_sql and not isinstance(count_sql, Composable):
            count_sql = SQL(count_sql)

        if count_sql_vars and not isinstance(count_sql_vars, (list, dict)):
            raise TypeError

        order = self.get_ordering(request)

        if order:
            nulls_last = SQL("NULLS LAST" if self.order_nulls_last else "")
            if order.startswith("-"):
                raw_sql = SQL("{} ORDER BY {} DESC {}").format(
                    raw_sql, Identifier(order[1:]), nulls_last
                )
            else:
                raw_sql = SQL("{} ORDER BY {} ASC {}").format(
                    raw_sql, Identifier(order), nulls_last
                )

        queryset = (raw_sql, sql_vars)
        count_query = (count_sql, count_sql_vars)
        page = self.paginate_queryset(queryset, count_query)
        additional_data = self.get_additional_data(page, **kwargs)

        if hasattr(self, "serialize_data"):
            page = self.serialize_data(page)

        return self.paginator.get_paginated_response(page, additional_data)


def _get_module(version, network):
    module_path = ".".join([version.lower(), network.lower()])
    module = importlib.import_module("ajna.{}.chain".format(module_path))
    return module


def _get_path_parts(request):
    version, network = request.path.lstrip("/").rstrip("/").split("/")[:2]

    if version not in AJNA_DEPLOYMENTS:
        raise Http404("Invalid path")

    if network not in AJNA_DEPLOYMENTS[version]:
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
                raise ValidationError("Wrong value for days_ago") from None

            if self.days_ago_options and self.days_ago not in self.days_ago_options:
                raise ValidationError("Wrong value for days_ago")

        elif self.days_ago_required:
            raise ValidationError("days_ago is a required param")

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self._handle_days_ago(request)


class BaseChainMixin:
    _chain = None

    @property
    def chain(self):
        if not self._chain:
            module = _get_module(self.protocol_version, self.protocol_network)
            cls_name = self.protocol_network.capitalize()
            cls = getattr(module, cls_name)
            self._chain = cls()
        return self._chain

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.protocol_version, self.protocol_network = _get_path_parts(request)
        self.models = ModelMapping(self.protocol_version, self.protocol_network)


class BaseChainView(DaysAgoMixin, BaseChainMixin, APIView):
    pass


class RawSQLPaginatedChainView(DaysAgoMixin, BaseChainMixin, RawSQLPaginatedApiView):
    pass
