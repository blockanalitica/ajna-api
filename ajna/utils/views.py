from hashlib import md5

from django.conf import settings
from django.core.cache import cache
from django.core.paginator import Paginator as DefaultPaginator
from django.db import connection
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from psycopg2.sql import SQL, Composable, Identifier, Literal
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from ajna.utils.db import fetch_all


class Pagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "p_size"
    max_page_size = 1000
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


class PaginatedApiView(APIView):
    ordering_fields = []
    search_fields = []
    default_order = None
    serializer_class = None
    model = None
    lookup_field = None
    queryset_extra = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.paginator = Pagination()
        ordering_fields = getattr(self, "ordering_fields", [])
        self.ordering_fields = []
        for field in ordering_fields:
            self.ordering_fields.append(field)
            self.ordering_fields.append("-{}".format(field))

        self.default_order = getattr(self, "default_order", None)

    def get_queryset(self, **kwargs):
        raise NotImplementedError

    def get_search_filters(self, request):
        search = request.query_params.get("search")
        filters = Q()
        if search:
            for field in self.search_fields:
                filters |= Q(**{"{}__icontains".format(field): search})
        return filters

    def get_ordering(self, request):
        param = request.query_params.get("order")
        if param in self.ordering_fields:
            return param
        return self.default_order

    def paginate_queryset(self, queryset):
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_additional_data(self, queryset, **kwargs):
        return {}

    def get(self, request, **kwargs):
        if self.model:
            filter_kwargs = {self.lookup_field: kwargs[self.lookup_field]}
            obj = get_object_or_404(self.model, **filter_kwargs)
            if self.queryset_extra:
                for extra in self.queryset_extra:
                    kwargs[extra] = getattr(obj, extra)

        search_filters = self.get_search_filters(request)
        queryset = self.get_queryset(
            search_filters=search_filters, query_params=request.GET, **kwargs
        )
        order = self.get_ordering(request)
        if order:
            queryset = queryset.order_by(order)

        page = self.paginate_queryset(queryset)
        if page is not None:
            if self.serializer_class:
                serializer = self.serializer_class(page, many=True)
                page = serializer.data
            additional_data = self.get_additional_data(queryset, **kwargs)
            return self.paginator.get_paginated_response(page, additional_data)
        if self.serializer_class:
            serializer = self.serializer_class(queryset, many=True)
            queryset = serializer.data
        return Response(queryset)


class RawQuerySetPaginator(DefaultPaginator):
    def __init__(self, sql, per_page, orphans=0, allow_empty_first_page=True):
        self.raw_sql, self.sql_vars = sql
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

        with connection.cursor() as cursor:
            cursor.execute(query_with_limit, self.sql_vars)
            results = fetch_all(cursor)

        return self._get_page(results, number, self)

    @cached_property
    def count(self):
        cache_key = None
        if settings.CACHE_RAW_SQL_PAGINATION_COUNT_SECONDS:
            cache_key = "RawQuerySetPaginator.count.{}".format(
                md5(
                    "|".join(str(x) for x in ([self.raw_sql] + self.sql_vars)).encode(
                        "utf-8"
                    )
                ).hexdigest()
            )
            cnt = cache.get(cache_key)
            if cnt is not None:
                return cnt

        count_query = SQL("SELECT COUNT(*) FROM ({}) AS count_sub_query").format(
            self.raw_sql
        )

        with connection.cursor() as cursor:
            cursor.execute(count_query, self.sql_vars)
            count = cursor.fetchone()[0]

        if cache_key:
            cache.set(cache_key, count, settings.CACHE_RAW_SQL_PAGINATION_COUNT_SECONDS)

        return count

    def _check_object_list_is_ordered(self):
        pass


class RawPagination(Pagination):
    django_paginator_class = RawQuerySetPaginator


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
        ordering_fields = getattr(self, "ordering_fields", [])
        self.ordering_fields = []
        for field in ordering_fields:
            self.ordering_fields.append(field)
            self.ordering_fields.append("-{}".format(field))

        self.default_order = getattr(self, "default_order", None)

    def get_queryset(self, **kwargs):
        raise InvalidMethod(
            "RawSQLPaginatedApiView needs get_raw_sql to be implemented instead of "
            "get_queryset"
        )

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
            return "({})".format(" OR ".join(filters)), [search] * len(
                self.search_fields
            )
        return None

    def get_ordering(self, request):
        param = request.query_params.get("order")
        if param in self.ordering_fields:
            return param
        return self.default_order

    def paginate_queryset(self, queryset):
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_additional_data(self, data, **kwargs):
        return {}

    def get(self, request, **kwargs):
        search_filters = self.get_search_filters(request)
        raw_sql, sql_vars = self.get_raw_sql(
            search_filters=search_filters, query_params=request.GET, **kwargs
        )
        if not isinstance(raw_sql, Composable):
            raw_sql = SQL(raw_sql)

        if sql_vars:
            assert isinstance(sql_vars, list)

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
        page = self.paginate_queryset(queryset)
        additional_data = self.get_additional_data(page, **kwargs)
        if self.serializer_class:
            serializer = self.serializer_class(page, many=True)
            page = serializer.data
        return self.paginator.get_paginated_response(page, additional_data)
