from datetime import date, timedelta

from django.http import Http404
from rest_framework import status
from rest_framework.response import Response

from ajna.constants import MAX_INFLATED_PRICE
from ajna.utils.db import fetch_all, fetch_one
from ajna.utils.views import BaseChainView, RawSQLPaginatedChainView

from ..modules.at_risk import WALLETS_AT_RISK_SQL
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
                , x.in_liquidation
                , x.tokens
                , x.token_addresses
            FROM (
                SELECT
                      cwp.wallet_address
                    , SUM(cwp.collateral * ct.underlying_price) AS collateral_usd
                    , SUM(cwp.t0debt * p.pending_inflator * qt.underlying_price) AS debt_usd
                    , BOOL_OR(cwp.in_liquidation) AS in_liquidation
                    , ARRAY_AGG(DISTINCT qt.symbol) AS tokens
                    , ARRAY_AGG(DISTINCT qt.underlying_address) AS token_addresses
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
                , x.tokens
                , x.token_addresses
            FROM (
                SELECT
                      cwp.wallet_address
                    , SUM(cwp.supply * qt.underlying_price) AS supply_usd
                    , ARRAY_AGG(DISTINCT qt.symbol) AS tokens
                    , ARRAY_AGG(DISTINCT qt.underlying_address) AS token_addresses
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
    days_ago_default = 1
    days_ago_options = [1, 7, 30, 90, 365, 9999]

    def _get_current(self, address):
        sql = """
            WITH previous_pools AS (
                SELECT DISTINCT ON (ps.address)
                      ps.address
                    , ps.quote_token_price
                    , ps.collateral_token_price
                    , ps.pending_inflator
                FROM {pool_snapshot_table} ps
                WHERE ps.datetime > (%s - INTERVAL '7 DAY')
                    AND ps.datetime <= %s
                ORDER BY ps.address, ps.datetime DESC
            ),
            previous AS (
                SELECT
                      wpx.wallet_address
                    , SUM(wpx.supply * p.quote_token_price) AS supply_usd
                    , SUM(wpx.collateral * p.collateral_token_price) AS collateral_usd
                    , SUM(wpx.t0debt * p.pending_inflator * p.quote_token_price) AS debt_usd
                FROM (
                    SELECT DISTINCT ON (wp.pool_address)
                          wp.pool_address
                        , wp.wallet_address
                        , wp.supply
                        , wp.collateral
                        , wp.t0debt
                    FROM {wallet_position_table} wp
                    WHERE wp.wallet_address = %s
                        AND wp.datetime <= %s
                    ORDER BY wp.pool_address, wp.datetime DESC
                ) wpx
                JOIN previous_pools p
                    ON wpx.pool_address = p.address
                GROUP BY 1
            )

            SELECT
              x.address
            , x.last_activity
            , x.first_activity
            , x.eoa
            , x.supply_usd
            , x.collateral_usd
            , x.debt_usd
            , prev.supply_usd AS prev_supply_usd
            , prev.collateral_usd AS prev_collateral_usd
            , prev.debt_usd AS prev_debt_usd
            FROM (
                SELECT
                      w.address
                    , w.last_activity
                    , w.first_activity
                    , w.eoa
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
                GROUP BY 1,2,3,4
            ) x
            LEFT JOIN previous AS prev
                ON x.address = prev.wallet_address
        """.format(
            wallet_table=self.models.wallet._meta.db_table,
            current_wallet_position_table=self.models.current_wallet_position._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
            wallet_position_table=self.models.wallet_position._meta.db_table,
            pool_snapshot_table=self.models.pool_snapshot._meta.db_table,
        )

        sql_vars = [
            self.days_ago_dt,
            self.days_ago_dt,
            address,
            self.days_ago_dt,
            address,
        ]
        wallet = fetch_one(sql, sql_vars)
        return wallet

    def _get_for_block(self, address, block_number):
        date_sql = """
            SELECT pe.block_datetime
            FROM {pool_event_table} pe
            WHERE pe.wallet_addresses @> ARRAY[%s]::varchar[]
                AND pe.block_number <= %s
            ORDER BY pe.block_datetime DESC
            LIMIT 1
        """.format(
            pool_event_table=self.models.pool_event._meta.db_table,
        )
        date_data = fetch_one(date_sql, [address, block_number])
        dt = date_data["block_datetime"]

        sql = """
            WITH previous_pools AS (
                SELECT DISTINCT ON (ps.address)
                      ps.address
                    , ps.quote_token_price
                    , ps.collateral_token_price
                    , ps.pending_inflator
                FROM {pool_snapshot_table} ps
                WHERE ps.datetime > (%(dt)s - INTERVAL '7 DAY')
                    AND ps.datetime <= %(dt)s
                ORDER BY ps.address, ps.datetime DESC
            ),

            positions AS (
                SELECT DISTINCT ON (wp.pool_address)
                      wp.wallet_address
                    , wp.pool_address
                    , wp.supply
                    , wp.collateral
                    , wp.t0debt
                FROM {wallet_position_table} wp
                WHERE wp.wallet_address = %(address)s
                    AND wp.block_number <= %(block_number)s
                ORDER BY wp.pool_address, wp.block_number DESC
            )

            SELECT
                  x.address
                , x.last_activity
                , x.first_activity
                , x.supply_usd
                , x.collateral_usd
                , x.debt_usd
            FROM (
                SELECT
                      w.address
                    , w.last_activity
                    , w.first_activity
                    , SUM(wp.supply * p.quote_token_price) AS supply_usd
                    , SUM(wp.collateral * p.collateral_token_price) AS collateral_usd
                    , SUM(wp.t0debt * p.pending_inflator * p.quote_token_price) AS debt_usd
                FROM {wallet_table} w
                LEFT JOIN positions AS wp
                    ON w.address = wp.wallet_address
                JOIN previous_pools p
                    ON wp.pool_address = p.address
                WHERE w.address = %(address)s
                GROUP BY 1,2,3
            ) x
        """.format(
            wallet_table=self.models.wallet._meta.db_table,
            wallet_position_table=self.models.wallet_position._meta.db_table,
            pool_snapshot_table=self.models.pool_snapshot._meta.db_table,
        )

        sql_vars = {"address": address, "block_number": block_number, "dt": dt}
        wallet = fetch_one(sql, sql_vars)
        return wallet

    def get(self, request, address):
        block = request.GET.get("block")
        if block:
            try:
                block = int(block)
            except ValueError:
                raise Http404 from None
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
        block = self.request.GET.get("block")
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
                , p.collateral_token_symbol
                , p.collateral_token_address
                , p.quote_token_symbol
                , p.quote_token_address
            FROM {pool_event_table} pe
            JOIN {pool_table} p
                ON pe.pool_address = p.address
            WHERE pe.wallet_addresses @> ARRAY[%s]::varchar[]
        """.format(
            pool_event_table=self.models.pool_event._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
        )

        sql_vars = [address]

        if event_name:
            sql = "{} AND pe.name = %s".format(sql)
            sql_vars.append(event_name)

        if block:
            sql = "{} AND pe.block_number <= %s".format(sql)
            sql_vars.append(block)

        return sql, sql_vars

    def serialize_data(self, data):
        for row in data:
            row["data"] = parse_event_data(row, self.chain)
        return data


class WalletPoolsView(RawSQLPaginatedChainView):
    days_ago_required = False
    days_ago_default = 7
    days_ago_options = [1, 7, 30, 90, 365, 9999]
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
            WITH previous_pools AS (
                SELECT DISTINCT ON (ps.address)
                      ps.address
                    , ps.quote_token_price
                    , ps.collateral_token_price
                    , ps.pending_inflator
                FROM {pool_snapshot_table} ps
                WHERE ps.datetime > (%s - INTERVAL '7 DAY')
                    AND ps.datetime <= %s
                ORDER BY ps.address, ps.datetime DESC
            ),
            previous AS (
                SELECT DISTINCT ON (wp.pool_address)
                      wp.pool_address
                    , wp.wallet_address
                    , wp.supply
                    , wp.supply * p.quote_token_price AS supply_usd
                    , wp.collateral
                    , wp.collateral * p.collateral_token_price AS collateral_usd
                    , wp.t0debt * p.pending_inflator AS debt
                    , wp.t0debt * p.pending_inflator * p.quote_token_price AS debt_usd
                FROM {wallet_position_table} wp
                LEFT JOIN previous_pools p
                    ON p.address = wp.pool_address
                WHERE wp.wallet_address = %s
                    AND wp.datetime <= %s
                ORDER BY wp.pool_address, wp.datetime DESC
            ),
            buckets AS (
                SELECT
                      b.pool_address
                    , SUM(b.deposit + b.collateral * b.bucket_price) AS total
                FROM {bucket_table} b
                GROUP BY 1
            )

            SELECT
                  x.wallet_address
                , x.pool_address
                , x.in_liquidation
                , x.supply
                , x.supply_usd
                , x.collateral
                , x.collateral_usd
                , x.debt
                , x.debt_usd
                , x.collateral_token_symbol
                , x.collateral_token_address
                , x.quote_token_symbol
                , x.quote_token_address
                , CASE
                    WHEN NULLIF(x.collateral, 0) IS NULL
                        OR NULLIF(x.debt, 0) IS NULL
                    THEN NULL
                    ELSE
                        CASE
                            WHEN x.lup / (x.debt / x.collateral) > 1000
                            THEN 1000
                            ELSE x.lup / (x.debt / x.collateral * 1.04)
                        END
                  END AS health_rate
                , CASE
                    WHEN NULLIF(x.pool_debt, 0) IS NULL
                        OR NULLIF(x.debt, 0) IS NULL
                    THEN NULL
                    ELSE x.debt / x.pool_debt
                  END AS debt_share
                , CASE
                    WHEN NULLIF(x.supply, 0) IS NULL
                        OR NULLIF(b.total, 0) IS NULL
                    THEN NULL
                    ELSE x.supply / b.total
                  END AS supply_share
                , prev.supply AS prev_supply
                , prev.supply_usd AS prev_supply_usd
                , prev.collateral AS prev_collateral
                , prev.collateral_usd AS prev_collateral_usd
                , prev.debt AS prev_debt
                , prev.debt_usd AS prev_debt_usd
            FROM (
                SELECT
                      cwp.wallet_address
                    , cwp.pool_address
                    , cwp.in_liquidation
                    , cwp.supply
                    , cwp.supply * qt.underlying_price AS supply_usd
                    , cwp.collateral
                    , cwp.collateral * ct.underlying_price as collateral_usd
                    , cwp.t0debt * p.pending_inflator AS debt
                    , cwp.t0debt * p.pending_inflator * qt.underlying_price AS debt_usd
                    , ct.symbol AS collateral_token_symbol
                    , ct.underlying_address as collateral_token_address
                    , qt.symbol AS quote_token_symbol
                    , qt.underlying_address AS quote_token_address
                    , p.t0debt * p.pending_inflator AS pool_debt
                    , p.lup
                    , p.pool_size
                    , qt.underlying_price AS quote_token_price
                    , ct.underlying_price AS collateral_token_price
                FROM {current_wallet_position_table} cwp
                JOIN {pool_table} p
                    ON cwp.pool_address = p.address
                JOIN {token_table} AS ct
                    ON p.collateral_token_address = ct.underlying_address
                JOIN {token_table} AS qt
                    ON p.quote_token_address = qt.underlying_address
                WHERE cwp.wallet_address = %s
            ) x
            LEFT JOIN previous AS prev
                ON x.wallet_address = prev.wallet_address
                    AND x.pool_address = prev.pool_address
            LEFT JOIN buckets AS b
                ON x.pool_address = b.pool_address
        """.format(
            current_wallet_position_table=self.models.current_wallet_position._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
            wallet_position_table=self.models.wallet_position._meta.db_table,
            pool_snapshot_table=self.models.pool_snapshot._meta.db_table,
            bucket_table=self.models.bucket._meta.db_table,
        )

        sql_vars = [
            self.days_ago_dt,
            self.days_ago_dt,
            address,
            self.days_ago_dt,
            address,
        ]
        return sql, sql_vars

    def _get_for_block(self, address, block):
        date_sql = """
            SELECT pe.block_datetime
            FROM {pool_event_table} pe
            WHERE pe.wallet_addresses @> ARRAY[%s]::varchar[]
                AND pe.block_number <= %s
            ORDER BY pe.block_datetime DESC
            LIMIT 1
        """.format(
            pool_event_table=self.models.pool_event._meta.db_table,
        )
        date_data = fetch_one(date_sql, [address, block])
        dt = date_data["block_datetime"]

        sql = """
            WITH previous_pools AS (
                SELECT DISTINCT ON (ps.address)
                      ps.address
                    , ps.quote_token_price
                    , ps.collateral_token_price
                    , ps.pending_inflator
                    , ps.collateral_token_address
                    , ps.quote_token_address
                    , ps.debt
                    , ps.lup
                FROM {pool_snapshot_table} ps
                WHERE ps.datetime > (%s - INTERVAL '7 DAY')
                    AND ps.datetime <= %s
                ORDER BY ps.address, ps.datetime DESC
            ),
            positions AS (
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
                , x.collateral_token_address
                , x.quote_token_symbol
                , x.quote_token_address
                , NULL AS health_rate
                , NULL AS debt_share
                , NULL AS supply_share
            FROM (
                SELECT
                      wp.wallet_address
                    , wp.pool_address
                    , wp.supply
                    , wp.supply * p.quote_token_price AS supply_usd
                    , wp.collateral
                    , wp.collateral * p.collateral_token_price as collateral_usd
                    , wp.t0debt * p.pending_inflator AS debt
                    , wp.t0debt * p.pending_inflator * p.quote_token_price AS debt_usd
                    , ct.symbol AS collateral_token_symbol
                    , ct.underlying_address AS collateral_token_address
                    , qt.symbol AS quote_token_symbol
                    , qt.underlying_address AS quote_token_address
                    , p.debt * p.quote_token_price AS pool_debt_usd
                    , p.lup
                FROM positions wp
                JOIN previous_pools p
                    ON wp.pool_address = p.address
                JOIN {token_table} AS ct
                    ON p.collateral_token_address = ct.underlying_address
                JOIN {token_table} AS qt
                    ON p.quote_token_address = qt.underlying_address
                WHERE wp.wallet_address = %s
            ) x
        """.format(
            wallet_position_table=self.models.wallet_position._meta.db_table,
            token_table=self.models.token._meta.db_table,
            pool_snapshot_table=self.models.pool_snapshot._meta.db_table,
        )

        sql_vars = [dt, dt, address, block, address]
        return sql, sql_vars

    def get_raw_sql(self, address, **kwargs):
        block = self.request.GET.get("block")
        if block:
            return self._get_for_block(address, block)
        else:
            return self._get_current(address)


class WalletPoolView(BaseChainView):
    days_ago_required = False
    days_ago_default = 1
    days_ago_options = [1, 7, 30, 90, 365, 9999]

    def get(self, request, address, pool_address):
        sql = """
            WITH previous_pools AS (
                SELECT DISTINCT ON (ps.address)
                      ps.address
                    , ps.quote_token_price
                    , ps.collateral_token_price
                    , ps.pending_inflator
                FROM {pool_snapshot_table} ps
                WHERE ps.datetime > (%(days_ago_dt)s - INTERVAL '7 DAY')
                    AND ps.datetime <= %(days_ago_dt)s
                    AND ps.address = %(pool_address)s
                ORDER BY ps.address, ps.datetime DESC
            ),
            previous AS (
                SELECT DISTINCT ON (wp.wallet_address)
                      wp.wallet_address
                    , wp.supply
                    , wp.supply * p.quote_token_price AS supply_usd
                    , wp.collateral
                    , wp.collateral * p.collateral_token_price AS collateral_usd
                    , wp.t0debt * p.pending_inflator AS debt
                    , wp.t0debt * p.pending_inflator * p.quote_token_price AS debt_usd
                FROM {wallet_position_table} wp
                LEFT JOIN previous_pools p
                    ON p.address = wp.pool_address
                WHERE wp.wallet_address = %(address)s
                    AND wp.pool_address = %(pool_address)s
                    AND wp.datetime <= %(days_ago_dt)s
                ORDER BY wp.wallet_address, wp.datetime DESC
            )

            SELECT
                  x.wallet_address
                , x.pool_address
                , x.in_liquidation
                , x.supply
                , x.supply_usd
                , x.collateral
                , x.collateral_usd
                , x.debt
                , x.debt_usd
                , x.collateral_token_symbol
                , x.collateral_token_address
                , x.quote_token_symbol
                , x.quote_token_address
                , x.lup
                , CASE
                    WHEN NULLIF(x.collateral, 0) IS NULL
                        OR NULLIF(x.debt, 0) IS NULL
                    THEN NULL
                    ELSE x.debt / x.collateral * 1.04
                  END AS threshold_price
                , CASE
                    WHEN NULLIF(x.collateral, 0) IS NULL
                        OR NULLIF(x.debt, 0) IS NULL
                    THEN NULL
                    ELSE LEAST((x.debt * 1.04) / x.collateral * x.np_tp_ratio, %(max_price)s)
                  END AS neutral_price
                , CASE
                    WHEN NULLIF(x.collateral, 0) IS NULL
                        OR NULLIF(x.debt, 0) IS NULL
                    THEN NULL
                    ELSE
                        CASE
                            WHEN x.lup / (x.debt / x.collateral) > 1000
                            THEN 1000
                            ELSE x.lup / (x.debt / x.collateral * 1.04)
                        END
                  END AS health_rate
                , CASE
                    WHEN NULLIF(x.pool_debt, 0) IS NULL
                        OR NULLIF(x.debt, 0) IS NULL
                    THEN NULL
                    ELSE x.debt / x.pool_debt
                  END AS debt_share
                , CASE
                    WHEN NULLIF(x.supply, 0) IS NULL
                        OR NULLIF(x.pool_size, 0) IS NULL
                    THEN NULL
                    ELSE x.supply / x.pool_size
                  END AS supply_share
                , x.prev_supply
                , x.prev_supply_usd
                , x.prev_collateral
                , x.prev_collateral_usd
                , x.prev_debt
                , x.prev_debt_usd
            FROM (
                SELECT
                      cwp.wallet_address
                    , cwp.pool_address
                    , cwp.in_liquidation
                    , cwp.supply
                    , cwp.supply * qt.underlying_price AS supply_usd
                    , cwp.collateral
                    , cwp.collateral * ct.underlying_price as collateral_usd
                    , cwp.t0debt * p.pending_inflator AS debt
                    , cwp.t0debt * p.pending_inflator * qt.underlying_price AS debt_usd
                    , cwp.np_tp_ratio
                    , ct.symbol AS collateral_token_symbol
                    , ct.underlying_address AS collateral_token_address
                    , qt.symbol AS quote_token_symbol
                    , qt.underlying_address AS quote_token_address
                    , p.t0debt * p.pending_inflator AS pool_debt
                    , p.lup
                    , p.pool_size
                    , prev.supply AS prev_supply
                    , prev.supply_usd AS prev_supply_usd
                    , prev.collateral AS prev_collateral
                    , prev.collateral_usd AS prev_collateral_usd
                    , prev.debt AS prev_debt
                    , prev.debt_usd AS prev_debt_usd
                FROM {current_wallet_position_table} cwp
                JOIN {pool_table} p
                    ON cwp.pool_address = p.address
                JOIN {token_table} AS ct
                    ON p.collateral_token_address = ct.underlying_address
                JOIN {token_table} AS qt
                    ON p.quote_token_address = qt.underlying_address
                LEFT JOIN previous AS prev
                    ON cwp.wallet_address = prev.wallet_address
                WHERE cwp.wallet_address = %(address)s
                    AND cwp.pool_address = %(pool_address)s
            ) x
        """.format(
            current_wallet_position_table=self.models.current_wallet_position._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
            wallet_position_table=self.models.wallet_position._meta.db_table,
            pool_snapshot_table=self.models.pool_snapshot._meta.db_table,
        )

        sql_vars = {
            "address": address,
            "pool_address": pool_address,
            "days_ago_dt": self.days_ago_dt,
            "max_price": MAX_INFLATED_PRICE,
        }
        wallet = fetch_one(sql, sql_vars)

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
        """.format(wallet_position_table=self.models.wallet_position._meta.db_table)

        sql_vars = [address, pool_address]

        history = fetch_all(sql, sql_vars)

        return Response(history, status.HTTP_200_OK)


class WalletPoolEventsView(RawSQLPaginatedChainView):
    default_order = "-order_index"
    ordering_fields = ["order_index"]

    def get_raw_sql(self, address, pool_address, query_params, **kwargs):
        event_name = query_params.get("name")
        sql = """
            SELECT
                  pe.block_number
                , pe.pool_address
                , pe.block_datetime
                , pe.transaction_hash
                , pe.name
                , pe.data
                , pe.collateral_token_price
                , pe.quote_token_price
                , pe.order_index
                , p.quote_token_symbol
                , p.quote_token_address
                , p.collateral_token_symbol
                , p.collateral_token_address
            FROM {pool_event_table} pe
            JOIN {pool_table} p
                ON pe.pool_address = p.address
            WHERE pe.wallet_addresses @> ARRAY[%s]::varchar[]
                AND pe.pool_address = %s
        """.format(
            pool_event_table=self.models.pool_event._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
        )

        sql_vars = [address, pool_address]

        if event_name:
            sql = "{} AND pe.name = %s".format(sql)
            sql_vars.append(event_name)

        return sql, sql_vars

    def serialize_data(self, data):
        for row in data:
            row["data"] = parse_event_data(row, self.chain)
        return data


class WalletPoolBucketsView(RawSQLPaginatedChainView):
    def get_raw_sql(self, address, pool_address, query_params, **kwargs):
        sql = """
            SELECT
                  x.bucket_index
                , x.deposit
                , x.bucket_price
            FROM (
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
                ORDER BY wbs.bucket_index, wbs.block_number DESC
            ) x
            WHERE x.deposit > 0
        """.format(
            wallet_bucket_state_table=self.models.wallet_bucket_state._meta.db_table,
            bucket_table=self.models.bucket._meta.db_table,
        )

        sql_vars = [address, pool_address]
        return sql, sql_vars


class WalletsAtRiskView(RawSQLPaginatedChainView):
    order_nulls_last = True
    default_order = "-price_change"
    ordering_fields = ["price_change", "debt", "collateral", "lup", "last_activity"]

    def get_raw_sql(self, query_params, **kwargs):
        try:
            change = int(query_params.get("change"))
        except (TypeError, ValueError):
            change = -5

        price_change = change / 100

        sql = WALLETS_AT_RISK_SQL.format(
            current_wallet_position_table=self.models.current_wallet_position._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
            wallet_table=self.models.wallet._meta.db_table,
        )

        return sql, [MAX_INFLATED_PRICE, price_change]


class WalletActivityHeatmapView(BaseChainView):
    days_ago_required = False
    days_ago_default = 365
    days_ago_options = [30, 90, 180, 365]

    def get(self, request, address):
        sql = """
            SELECT
                  DATE_TRUNC('day', pe.block_datetime) AS date
                , COUNT(*) AS value
            FROM {pool_event_table} pe
            WHERE pe.wallet_addresses @> ARRAY[%s]::varchar[]
                AND pe.block_datetime > %s
            GROUP BY 1
        """.format(
            pool_event_table=self.models.pool_event._meta.db_table,
        )

        # We always need to select data from the start of the week
        dt = date.today() - timedelta(days=self.days_ago)
        dt = dt - timedelta(days=dt.weekday())
        sql_vars = [address, dt]

        data = fetch_all(sql, sql_vars)
        return Response(data, status.HTTP_200_OK)
