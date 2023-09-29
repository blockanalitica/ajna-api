from django.db import connection
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response

from ajna.utils.db import fetch_one, fetch_all
from ajna.utils.views import BaseChainView, RawSQLPaginatedChainView

from ..modules.events import parse_event_data


class WalletsView(RawSQLPaginatedChainView):
    order_nulls_last = True
    search_fields = ["x.wallet_address"]

    def _get_borrowers_sql(self):
        return """
            SELECT
                  x.wallet_address
                , x.collateral_usd
                , x.debt_usd
                , w.last_activity
                , w.first_activity
            FROM (
                SELECT
                      cwp.wallet_address
                    , SUM(cwp.collateral * ct.underlying_price) AS collateral_usd
                    , SUM(cwp.t0debt * p.pending_inflator * qt.underlying_price) AS debt_usd
                FROM {current_wallet_position_table} cwp
                JOIN {pool_table} p
                    ON cwp.pool_address = p.address
                JOIN {token_table} AS ct
                    ON p.collateral_token_address = ct.underlying_address
                JOIN {token_table} AS qt
                    ON p.quote_token_address = qt.underlying_address
                WHERE (cwp.t0debt > 0 OR cwp.collateral > 0)
                GROUP BY 1
            ) x
            JOIN {wallet_table} as w
                ON x.wallet_address = w.address
        """.format(
            current_wallet_position_table=self.models.current_wallet_position._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
            wallet_table=self.models.wallet._meta.db_table,
        )

    def _get_depositors_sql(self):
        return """
            SELECT
                  x.wallet_address
                , x.supply_usd
                , w.last_activity
                , w.first_activity
            FROM (
                SELECT
                      cwp.wallet_address
                    , SUM(cwp.supply * qt.underlying_price) AS supply_usd
                FROM {current_wallet_position_table} cwp
                JOIN {pool_table} p
                    ON cwp.pool_address = p.address
                JOIN {token_table} AS ct
                    ON p.collateral_token_address = ct.underlying_address
                JOIN {token_table} AS qt
                    ON p.quote_token_address = qt.underlying_address
                WHERE cwp.supply > 0
                GROUP BY 1
            ) x
            JOIN {wallet_table} as w
                ON x.wallet_address = w.address
        """.format(
            current_wallet_position_table=self.models.current_wallet_position._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
            wallet_table=self.models.wallet._meta.db_table,
        )

    def get_raw_sql(self, search_filters, query_params, **kwargs):
        wallet_type = query_params.get("type")

        if wallet_type == "depositors":
            sql = self._get_depositors_sql()
            self.ordering_fields = ["last_activity", "first_activity", "supply_usd"]
        else:
            sql = self._get_borrowers_sql()
            self.ordering_fields = [
                "last_activity",
                "first_activity",
                "debt_usd",
                "collateral_usd",
            ]

        sql_vars = []
        filters = []
        if search_filters:
            search_sql, search_vars = search_filters
            filters.append(search_sql)
            sql_vars.extend(search_vars)

        if filters:
            sql += " WHERE {}".format(" AND ".join(filters))

        return sql, sql_vars


class WalletView(BaseChainView):
    days_ago_required = False
    days_ago_default = 7
    days_ago_options = [1, 7, 30, 365]

    def _get_current(self, address):
        sql = """
            SELECT
              x.address
            , x.last_activity
            , x.first_activity
            , x.supply_usd
            , x.collateral_usd
            , x.debt_usd
            , CASE
                WHEN NULLIF(x.collateral_usd, 0) IS NULL
                    OR NULLIF(x.debt_usd, 0) IS NULL
                THEN NULL
                ELSE
                    CASE
                        WHEN x.collateral_usd / x.debt_usd > 1000
                        THEN 1000
                        ELSE x.collateral_usd / x.debt_usd
                    END
              END AS health_rate
            FROM (
                SELECT
                      w.address
                    , w.last_activity
                    , w.first_activity
                    , SUM(cwp.supply * qt.underlying_price) AS supply_usd
                    , SUM(cwp.collateral * ct.underlying_price) AS collateral_usd
                    , SUM(cwp.t0debt * p.pending_inflator * qt.underlying_price) AS debt_usd
                FROM {wallet_table} w
                LEFT JOIN {current_wallet_position_table} cwp
                    ON w.address = cwp.wallet_address
                JOIN {pool_table} p
                    ON cwp.pool_address = p.address
                JOIN {token_table} AS ct
                    ON p.collateral_token_address = ct.underlying_address
                JOIN {token_table} AS qt
                    ON p.quote_token_address = qt.underlying_address
                WHERE w.address = %s
                GROUP BY 1,2,3
            ) x
        """.format(
            wallet_table=self.models.wallet._meta.db_table,
            current_wallet_position_table=self.models.current_wallet_position._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
        )

        sql_vars = [address]
        with connection.cursor() as cursor:
            cursor.execute(sql, sql_vars)
            wallet = fetch_one(cursor)
        return wallet

    def _get_for_block(self, address, block_number):
        sql = """
            WITH positions AS (
                SELECT DISTINCT ON (wp.pool_address)
                    *
                FROM {wallet_position_table} wp
                WHERE wp.wallet_address = %s
                    AND wp.block_number <= %s
                ORDER BY wp.pool_address, wp.block_number DESC
            )
            
            SELECT
              x.address
            , x.last_activity
            , x.first_activity
            , x.supply_usd
            , x.collateral_usd
            , x.debt_usd
            , CASE
                WHEN NULLIF(x.collateral_usd, 0) IS NULL
                    OR NULLIF(x.debt_usd, 0) IS NULL
                THEN NULL
                ELSE
                    CASE
                        WHEN x.collateral_usd / x.debt_usd > 1000
                        THEN 1000
                        ELSE x.collateral_usd / x.debt_usd
                    END
              END AS health_rate
            FROM (
                SELECT
                      w.address
                    , w.last_activity
                    , w.first_activity
                    , SUM(wp.supply * qt.underlying_price) AS supply_usd
                    , SUM(wp.collateral * ct.underlying_price) AS collateral_usd
                    , SUM(wp.t0debt * p.pending_inflator * qt.underlying_price) AS debt_usd
                FROM {wallet_table} w
                LEFT JOIN positions AS wp
                    ON w.address = wp.wallet_address
                JOIN {pool_table} p
                    ON wp.pool_address = p.address
                JOIN {token_table} AS ct
                    ON p.collateral_token_address = ct.underlying_address
                JOIN {token_table} AS qt
                    ON p.quote_token_address = qt.underlying_address
                WHERE w.address = %s
                GROUP BY 1,2,3
            ) x
        """.format(
            wallet_table=self.models.wallet._meta.db_table,
            wallet_position_table=self.models.wallet_position._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
        )

        sql_vars = [address, block_number, address]
        with connection.cursor() as cursor:
            cursor.execute(sql, sql_vars)
            wallet = fetch_one(cursor)
        return wallet

    def get(self, request, address):
        block = request.GET.get("block")
        if block:
            wallet = self._get_for_block(address, block)
        else:
            wallet = self._get_current(address)

        if not wallet:
            raise Http404

        return Response(wallet, status.HTTP_200_OK)


class WalletEventsView(RawSQLPaginatedChainView):
    default_order = "-order_index"
    ordering_fields = ["order_index"]

    def get_raw_sql(self, address, query_params, **kwargs):
        event_name = query_params.get("name")
        sql = """
            SELECT
                  pe.pool_address
                , pe.block_number
                , pe.block_datetime
                , pe.transaction_hash
                , pe.name
                , pe.data
                , pe.collateral_token_price
                , pe.quote_token_price
                , pe.order_index
                , qt.symbol AS quote_token_symbol
                , ct.symbol AS collateral_token_symbol
            FROM {pool_event_table} pe
            JOIN {pool_table} p
                ON pe.pool_address = p.address
            JOIN {token_table} AS ct
                ON p.collateral_token_address = ct.underlying_address
            JOIN {token_table} AS qt
                ON p.quote_token_address = qt.underlying_address
            WHERE pe.wallet_addresses @> ARRAY[%s]::varchar[]
        """.format(
            pool_event_table=self.models.pool_event._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
        )

        sql_vars = [address]

        if event_name:
            sql = "{} AND pe.name = %s".format(sql)
            sql_vars.append(event_name)

        return sql, sql_vars

    def serialize_data(self, data):
        for row in data:
            row["data"] = parse_event_data(row)
        return data


class WalletPoolsView(RawSQLPaginatedChainView):
    default_order = "-debt"
    ordering_fields = [
        "supply",
        "collateral",
        "debt",
        "health_rate",
        "debt_share",
        "supply_share",
    ]

    def _get_current(self, address):
        sql = """
            SELECT
                  x.wallet_address
                , x.pool_address
                , x.supply
                , x.supply_usd
                , x.collateral
                , x.collateral_usd
                , x.debt
                , x.debt_usd
                , x.collateral_token_symbol
                , x.quote_token_symbol
                , CASE
                    WHEN NULLIF(x.collateral_usd, 0) IS NULL
                        OR NULLIF(x.debt_usd, 0) IS NULL
                    THEN NULL
                    ELSE
                        CASE
                            WHEN x.collateral_usd / x.debt_usd > 1000
                            THEN 1000
                            ELSE x.collateral_usd / x.debt_usd
                        END
                  END AS health_rate
                , CASE
                    WHEN NULLIF(x.pool_debt_usd, 0) IS NULL
                        OR NULLIF(x.debt_usd, 0) IS NULL
                    THEN NULL
                    ELSE x.debt_usd / x.pool_debt_usd
                  END AS debt_share
                , CASE
                    WHEN NULLIF(x.supply_usd, 0) IS NULL
                        OR NULLIF(x.pool_supply_usd, 0) IS NULL
                    THEN NULL
                    ELSE x.supply_usd / x.pool_supply_usd
                  END AS supply_share
            FROM (
                SELECT
                      cwp.wallet_address
                    , cwp.pool_address
                    , cwp.supply
                    , cwp.supply * qt.underlying_price AS supply_usd
                    , cwp.collateral
                    , cwp.collateral * ct.underlying_price as collateral_usd
                    , cwp.t0debt * p.pending_inflator AS debt
                    , cwp.t0debt * p.pending_inflator * qt.underlying_price AS debt_usd
                    , ct.symbol AS collateral_token_symbol
                    , qt.symbol AS quote_token_symbol
                    , p.t0debt * p.pending_inflator * qt.underlying_price AS pool_debt_usd
                    , p.pool_size * qt.underlying_price AS pool_supply_usd
                FROM {current_wallet_position_table} cwp
                JOIN {pool_table} p
                    ON cwp.pool_address = p.address
                JOIN {token_table} AS ct
                    ON p.collateral_token_address = ct.underlying_address
                JOIN {token_table} AS qt
                    ON p.quote_token_address = qt.underlying_address
                WHERE cwp.wallet_address = %s
            ) x
        """.format(
            current_wallet_position_table=self.models.current_wallet_position._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
        )

        sql_vars = [address]
        return sql, sql_vars

    def _get_for_block(self, address, block):
        sql = """
            WITH positions AS (
                SELECT DISTINCT ON (wp.pool_address)
                    *
                FROM {wallet_position_table} wp
                WHERE wp.wallet_address = %s
                    AND wp.block_number <= %s
                ORDER BY wp.pool_address, wp.block_number DESC
            )

            SELECT
                  x.wallet_address
                , x.pool_address
                , x.supply
                , x.supply_usd
                , x.collateral
                , x.collateral_usd
                , x.debt
                , x.debt_usd
                , x.collateral_token_symbol
                , x.quote_token_symbol
                , CASE
                    WHEN NULLIF(x.collateral_usd, 0) IS NULL
                        OR NULLIF(x.debt_usd, 0) IS NULL
                    THEN NULL
                    ELSE
                        CASE
                            WHEN x.collateral_usd / x.debt_usd > 1000
                            THEN 1000
                            ELSE x.collateral_usd / x.debt_usd
                        END
                  END AS health_rate
                , CASE
                    WHEN NULLIF(x.pool_debt_usd, 0) IS NULL
                        OR NULLIF(x.debt_usd, 0) IS NULL
                    THEN NULL
                    ELSE x.debt_usd / x.pool_debt_usd
                  END AS debt_share
                , CASE
                    WHEN NULLIF(x.supply_usd, 0) IS NULL
                        OR NULLIF(x.pool_supply_usd, 0) IS NULL
                    THEN NULL
                    ELSE x.supply_usd / x.pool_supply_usd
                  END AS supply_share
            FROM (
                SELECT
                      wp.wallet_address
                    , wp.pool_address
                    , wp.supply
                    , wp.supply * qt.underlying_price AS supply_usd
                    , wp.collateral
                    , wp.collateral * ct.underlying_price as collateral_usd
                    , wp.t0debt * p.pending_inflator AS debt
                    , wp.t0debt * p.pending_inflator * qt.underlying_price AS debt_usd
                    , ct.symbol AS collateral_token_symbol
                    , qt.symbol AS quote_token_symbol
                    , p.t0debt * p.pending_inflator * qt.underlying_price AS pool_debt_usd
                    , p.pool_size * qt.underlying_price AS pool_supply_usd
                FROM positions wp
                JOIN {pool_table} p
                    ON wp.pool_address = p.address
                JOIN {token_table} AS ct
                    ON p.collateral_token_address = ct.underlying_address
                JOIN {token_table} AS qt
                    ON p.quote_token_address = qt.underlying_address
                WHERE wp.wallet_address = %s
            ) x
        """.format(
            wallet_position_table=self.models.wallet_position._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
        )

        sql_vars = [address, block, address]
        return sql, sql_vars

    def get_raw_sql(self, address, **kwargs):
        block = self.request.GET.get("block")
        if block:
            return self._get_for_block(address, block)
        else:
            return self._get_current(address)


class WalletPoolView(BaseChainView):
    days_ago_required = False
    days_ago_default = 7
    days_ago_options = [1, 7, 30, 365]

    def get(self, request, address, pool_address):
        sql = """
            SELECT
                  x.wallet_address
                , x.pool_address
                , x.supply
                , x.supply_usd
                , x.collateral
                , x.collateral_usd
                , x.debt
                , x.debt_usd
                , x.collateral_token_symbol
                , x.quote_token_symbol
                , CASE
                    WHEN NULLIF(x.collateral_usd, 0) IS NULL
                        OR NULLIF(x.debt_usd, 0) IS NULL
                    THEN NULL
                    ELSE
                        CASE
                            WHEN x.collateral_usd / x.debt_usd > 1000
                            THEN 1000
                            ELSE x.collateral_usd / x.debt_usd
                        END
                  END AS health_rate
                , CASE
                    WHEN NULLIF(x.pool_debt_usd, 0) IS NULL
                        OR NULLIF(x.debt_usd, 0) IS NULL
                    THEN NULL
                    ELSE x.debt_usd / x.pool_debt_usd
                  END AS debt_share
                , CASE
                    WHEN NULLIF(x.supply_usd, 0) IS NULL
                        OR NULLIF(x.pool_supply_usd, 0) IS NULL
                    THEN NULL
                    ELSE x.supply_usd / x.pool_supply_usd
                  END AS supply_share
            FROM (
                SELECT
                      cwp.wallet_address
                    , cwp.pool_address
                    , cwp.supply
                    , cwp.supply * qt.underlying_price AS supply_usd
                    , cwp.collateral
                    , cwp.collateral * ct.underlying_price as collateral_usd
                    , cwp.t0debt * p.pending_inflator AS debt
                    , cwp.t0debt * p.pending_inflator * qt.underlying_price AS debt_usd
                    , ct.symbol AS collateral_token_symbol
                    , qt.symbol AS quote_token_symbol
                    , p.t0debt * p.pending_inflator * qt.underlying_price AS pool_debt_usd
                    , p.pool_size * qt.underlying_price AS pool_supply_usd
                FROM {current_wallet_position_table} cwp
                JOIN {pool_table} p
                    ON cwp.pool_address = p.address
                JOIN {token_table} AS ct
                    ON p.collateral_token_address = ct.underlying_address
                JOIN {token_table} AS qt
                    ON p.quote_token_address = qt.underlying_address
                WHERE cwp.wallet_address = %s
                    AND cwp.pool_address = %s
            ) x
        """.format(
            current_wallet_position_table=self.models.current_wallet_position._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
        )

        sql_vars = [address, pool_address]
        with connection.cursor() as cursor:
            cursor.execute(sql, sql_vars)
            wallet = fetch_one(cursor)

        if not wallet:
            raise Http404

        return Response(wallet, status.HTTP_200_OK)


class WalletPoolHistoricView(BaseChainView):
    def get(self, request, address, pool_address):
        sql = """
            SELECT DISTINCT ON (DATE_TRUNC('day', wp.datetime))
                  DATE_TRUNC('day', wp.datetime) AS date
                , wp.supply
                , wp.collateral
                , wp.t0debt as debt
            FROM {wallet_position_table} wp
            WHERE wp.wallet_address = %s
                AND wp.pool_address = %s
            ORDER BY 1, wp.datetime DESC
        """.format(
            wallet_position_table=self.models.wallet_position._meta.db_table
        )

        sql_vars = [address, pool_address]
        with connection.cursor() as cursor:
            cursor.execute(sql, sql_vars)
            history = fetch_all(cursor)

        return Response(history, status.HTTP_200_OK)


class WalletPoolEventsView(RawSQLPaginatedChainView):
    default_order = "-order_index"
    ordering_fields = ["order_index"]

    def get_raw_sql(self, address, pool_address, query_params, **kwargs):
        event_name = query_params.get("name")
        sql = """
            SELECT
                  pe.block_number
                , pe.block_datetime
                , pe.transaction_hash
                , pe.name
                , pe.data
                , pe.collateral_token_price
                , pe.quote_token_price
                , pe.order_index
                , qt.symbol AS quote_token_symbol
                , ct.symbol AS collateral_token_symbol
            FROM {pool_event_table} pe
            JOIN {pool_table} p
                ON pe.pool_address = p.address
            JOIN {token_table} AS ct
                ON p.collateral_token_address = ct.underlying_address
            JOIN {token_table} AS qt
                ON p.quote_token_address = qt.underlying_address
            WHERE pe.wallet_addresses @> ARRAY[%s]::varchar[]
                AND pe.pool_address = %s
        """.format(
            pool_event_table=self.models.pool_event._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
        )

        sql_vars = [address, pool_address]

        if event_name:
            sql = "{} AND pe.name = %s".format(sql)
            sql_vars.append(event_name)

        return sql, sql_vars

    def serialize_data(self, data):
        for row in data:
            row["data"] = parse_event_data(row)
        return data


class WalletPoolBucketsView(RawSQLPaginatedChainView):
    def get_raw_sql(self, address, pool_address, query_params, **kwargs):
        sql = """
            SELECT DISTINCT ON (wbs.bucket_index)
                  wbs.bucket_index
                , wbs.deposit
                , b.bucket_price
            FROM {wallet_bucket_state_table} wbs
            JOIN {bucket_table} b
                ON b.bucket_index = wbs.bucket_index
                AND b.pool_address = wbs.pool_address
            WHERE wbs.wallet_address = %s
                AND wbs.pool_address = %s
                AND wbs.deposit > 0
            ORDER BY wbs.bucket_index, wbs.block_number DESC
        """.format(
            wallet_bucket_state_table=self.models.wallet_bucket_state._meta.db_table,
            bucket_table=self.models.bucket._meta.db_table,
        )

        sql_vars = [address, pool_address]
        return sql, sql_vars
