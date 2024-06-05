from copy import deepcopy
from datetime import datetime, timedelta

from django.http import Http404
from rest_framework import status
from rest_framework.response import Response

from ajna.constants import MAX_INFLATED_PRICE
from ajna.utils.db import fetch_all, fetch_one
from ajna.utils.views import BaseChainView, RawSQLPaginatedChainView

from ..modules.at_risk import WALLETS_AT_RISK_SQL
from ..modules.auctions import calculate_current_auction_price
from ..modules.events import parse_event_data

POOLS_SQL = """
    WITH previous AS (
        SELECT DISTINCT ON (ps.address)
              ps.address
            , ps.pledged_collateral
            , ps.pledged_collateral * ps.collateral_token_price AS pledged_collateral_usd
            , ps.collateral_token_balance AS collateral
            , ps.collateral_token_balance * ps.collateral_token_balance AS collateral_usd
            , ps.pool_size
            , ps.pool_size * ps.quote_token_price AS pool_size_usd
            , ps.debt
            , ps.debt * ps.quote_token_price as debt_usd
            , ps.total_ajna_burned
            , ps.borrow_rate
            , ps.lend_rate
            , ps.reserves
            , ps.reserves * ps.quote_token_price as reserves_usd
            , ps.collateral_token_balance
            , ps.quote_token_balance
            , COALESCE(ps.collateral_token_balance * ps.collateral_token_price, 0) +
                COALESCE(ps.quote_token_balance * ps.quote_token_price, 0) AS tvl
        FROM {pool_snapshot_table} ps
        WHERE ps.datetime > (%s - INTERVAL '7 DAY') AND ps.datetime <= %s
        ORDER BY ps.address, ps.datetime DESC
    )

    SELECT
          pool.address
        , pool.quote_token_balance
        , pool.pledged_collateral
        , pool.pledged_collateral * collateral_token.underlying_price AS pledged_collateral_usd
        , pool.collateral_token_balance AS collateral
        , pool.collateral_token_balance * collateral_token.underlying_price AS collateral_usd
        , pool.pool_size
        , pool.pool_size * quote_token.underlying_price AS pool_size_usd
        , pool.t0debt * pool.pending_inflator as debt
        , pool.t0debt * pool.pending_inflator * quote_token.underlying_price AS debt_usd
        , pool.borrow_rate
        , pool.lend_rate
        , pool.total_ajna_burned
        , pool.erc
        , pool.reserves
        , pool.reserves * quote_token.underlying_price AS reserves_usd
        , pool.allowed_token_ids
        , collateral_token.symbol AS collateral_token_symbol
        , collateral_token.name AS collateral_token_name
        , collateral_token.underlying_address AS collateral_token_address
        , quote_token.symbol AS quote_token_symbol
        , quote_token.name AS quote_token_name
        , quote_token.underlying_address AS quote_token_address
        , COALESCE(pool.collateral_token_balance * collateral_token.underlying_price, 0) +
            COALESCE(pool.quote_token_balance * quote_token.underlying_price, 0) AS tvl
        , prev.pledged_collateral AS prev_pledged_collateral
        , prev.pledged_collateral_usd AS prev_pledged_collateral_usd
        , prev.collateral AS prev_collateral
        , prev.collateral_usd AS prev_collateral_usd
        , prev.pool_size AS prev_pool_size
        , prev.pool_size_usd AS prev_pool_size_usd
        , prev.debt AS prev_debt
        , prev.debt_usd AS prev_debt_usd
        , prev.total_ajna_burned AS prev_total_ajna_burned
        , prev.borrow_rate AS prev_borrow_rate
        , prev.lend_rate AS prev_lend_rate
        , prev.tvl AS prev_tvl
        , prev.reserves AS prev_reserves
        , prev.reserves_usd AS prev_reserves_usd
    FROM {pool_table} AS pool
    JOIN {token_table} AS collateral_token
        ON pool.collateral_token_address = collateral_token.underlying_address
    JOIN {token_table} AS quote_token
        ON pool.quote_token_address = quote_token.underlying_address
    LEFT JOIN previous AS prev
        ON pool.address = prev.address
"""


class PoolsView(RawSQLPaginatedChainView):
    order_nulls_last = True
    days_ago_required = False
    days_ago_default = 1
    days_ago_options = [1, 7, 30, 90, 365, 9999]
    default_order = "-tvl"
    ordering_fields = [
        "collateral",
        "collateral_usd",
        "pledged_collateral",
        "pledged_collateral_usd",
        "pool_size",
        "pool_size_usd",
        "debt",
        "debt_usd",
        "borrow_rate",
        "lend_rate",
        "total_ajna_burned",
        "tvl",
    ]
    search_fields = ["collateral_token.symbol", "quote_token.symbol"]

    def _get_new_events(self):
        event_name = "PoolCreated"
        date = datetime.now() - timedelta(days=1)
        sql = """
            SELECT
                p.pool_address
            FROM {pool_event_table} p
            WHERE p.name = %s AND p.block_datetime >= %s
        """.format(
            pool_event_table=self.models.pool_event._meta.db_table,
        )
        sql_vars = [event_name, date]
        pools = fetch_all(sql, sql_vars)
        pools_list = []
        for pool in pools:
            pools_list.append(pool["pool_address"])

        return pools_list

    def _get_liquidation_pools(self):
        sql = WALLETS_AT_RISK_SQL.format(
            current_wallet_position_table=self.models.current_wallet_position._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
            wallet_table=self.models.wallet._meta.db_table,
        )
        sql_vars = [MAX_INFLATED_PRICE, 0]
        pools = fetch_all(sql, sql_vars)
        pools_list = []
        for pool in pools:
            pools_list.append(pool["pool_address"])

        return pools_list

    def get_raw_sql(self, search_filters, query_params, **kwargs):
        query_filters = query_params.get("filter")
        sql = POOLS_SQL.format(
            token_table=self.models.token._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            pool_snapshot_table=self.models.pool_snapshot._meta.db_table,
        )

        sql_vars = [self.days_ago_dt, self.days_ago_dt]
        filters = []
        if search_filters:
            search_sql, search_vars = search_filters
            filters.append(search_sql)
            sql_vars.extend(search_vars)
        if query_filters == "new":
            pools = self._get_new_events()
            if pools:
                filters.append("pool.address IN %s")
                sql_vars.append(tuple(pools))
            else:
                filters.append("pool.address = 'xxx'")

        if query_filters == "arbitrage":
            filters.append(
                "pool.hpb * quote_token.underlying_price >= collateral_token.underlying_price"
            )

        if query_filters == "liquidation":
            pools = self._get_liquidation_pools()
            if pools:
                filters.append("pool.address IN %s")
                sql_vars.append(tuple(pools))
            else:
                filters.append("pool.address = 'xxx'")

        if filters:
            sql += " WHERE {}".format(" AND ".join(filters))

        return sql, sql_vars


class PoolView(BaseChainView):
    days_ago_required = False
    days_ago_default = 1
    days_ago_options = [1, 7, 30, 90, 365, 9999]

    def get(self, request, pool_address):
        sql_vars = [
            self.days_ago_dt,
            pool_address,
            pool_address,
        ]
        sql = """
            WITH
                previous AS (
                    SELECT DISTINCT ON (ps.address)
                        ps.address
                        , ps.pledged_collateral
                        , ps.pledged_collateral * ps.collateral_token_price
                            AS pledged_collateral_usd
                        , ps.collateral_token_balance AS collateral
                        , ps.collateral_token_balance * ps.collateral_token_balance
                            AS collateral_usd
                        , ps.pool_size
                        , ps.pool_size * ps.quote_token_price AS pool_size_usd
                        , ps.t0debt
                        , ps.debt
                        , ps.debt * ps.quote_token_price AS debt_usd
                        , ps.lup
                        , ps.htp
                        , ps.hpb
                        , ps.total_ajna_burned
                        , ps.quote_token_price
                        , ps.collateral_token_price
                        , ps.reserves
                        , ps.lend_rate
                        , ps.borrow_rate
                        , ps.actual_utilization
                        , ps.target_utilization
                        , COALESCE(ps.collateral_token_balance * ps.collateral_token_price, 0) +
                            COALESCE(ps.quote_token_balance * ps.quote_token_price, 0) AS tvl
                    FROM {pool_snapshot_table} ps
                    WHERE ps.datetime <= %s AND ps.address = %s
                    ORDER BY ps.address, ps.datetime DESC
                )

            SELECT
                  pool.address
                , pool.t0debt * pool.pending_inflator as debt
                , pool.quote_token_address
                , pool.collateral_token_address
                , pool.t0debt * pool.pending_inflator * quote_token.underlying_price as debt_usd
                , pool.pledged_collateral
                , pool.pledged_collateral * collateral_token.underlying_price
                    AS pledged_collateral_usd
                , pool.collateral_token_balance AS collateral
                , pool.collateral_token_balance * collateral_token.underlying_price
                    AS collateral_usd
                , pool.pool_size
                , pool.pool_size * quote_token.underlying_price AS pool_size_usd
                , pool.lup
                , pool.htp
                , pool.hpb
                , pool.lup_index
                , pool.htp_index
                , pool.hpb_index
                , pool.lend_rate
                , pool.borrow_rate
                , pool.total_ajna_burned
                , pool.min_debt_amount
                , pool.reserves
                , pool.volume_today AS volume
                , ((pool.pledged_collateral * collateral_token.underlying_price)
                    / NULLIF(
                        (pool.t0debt * pool.pending_inflator * quote_token.underlying_price), 0)
                    ) as collateralization
                , pool.utilization
                , pool.actual_utilization
                , pool.target_utilization
                , pool.quote_token_balance
                , pool.erc
                , pool.allowed_token_ids
                , pool.quote_token_balance * quote_token.underlying_price AS quote_token_balance_usd
                , collateral_token.symbol AS collateral_token_symbol
                , collateral_token.name AS collateral_token_name
                , collateral_token.underlying_price AS collateral_token_underlying_price
                , collateral_token.is_estimated_price AS collateral_token_is_estimated_price
                , quote_token.symbol AS quote_token_symbol
                , quote_token.name AS quote_token_name
                , quote_token.underlying_price AS quote_token_underlying_price
                , COALESCE(pool.collateral_token_balance * collateral_token.underlying_price, 0) +
                  COALESCE(pool.quote_token_balance * quote_token.underlying_price, 0) AS tvl
                , prev.tvl AS prev_tvl
                , prev.pledged_collateral AS prev_pledged_collateral
                , prev.collateral AS prev_collateral
                , prev.pool_size AS prev_pool_size
                , prev.debt as prev_debt
                , prev.pledged_collateral_usd AS prev_pledged_collateral_usd
                , prev.collateral_usd AS prev_collateral_usd
                , prev.pool_size_usd AS prev_pool_size_usd
                , prev.debt_usd as prev_debt_usd
                , prev.lup as prev_lup
                , prev.htp as prev_htp
                , prev.hpb as prev_hpb
                , prev.total_ajna_burned as prev_total_ajna_burned
                , prev.quote_token_price as prev_quote_token_price
                , prev.collateral_token_price as prev_collateral_token_price
                , prev.reserves as prev_reserves
                , prev.lend_rate as prev_lend_rate
                , prev.borrow_rate as prev_borrow_rate
                , prev.actual_utilization as prev_actual_utilization
                , prev.target_utilization as prev_target_utilization
            FROM {pool_table} AS pool
            JOIN {token_table} AS collateral_token
                ON pool.collateral_token_address = collateral_token.underlying_address
            JOIN {token_table} AS quote_token
                ON pool.quote_token_address = quote_token.underlying_address
            LEFT JOIN previous AS prev
                ON pool.address = prev.address
            WHERE pool.address = %s
        """.format(
            token_table=self.models.token._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            pool_snapshot_table=self.models.pool_snapshot._meta.db_table,
        )

        pool_data = fetch_one(sql, sql_vars)

        if not pool_data:
            raise Http404

        return Response({"results": pool_data}, status.HTTP_200_OK)


class PoolHistoricView(BaseChainView):
    """
    A view for retrieving historic information about a specific pool.
    """

    days_ago_required = False
    days_ago_default = 30
    days_ago_options = [30, 90, 365, 9999]

    def _get_tvl(self, pool_address):
        sql_vars = [self.days_ago_dt, pool_address]
        sql = """
            SELECT DISTINCT ON (DATE_TRUNC('day', ps.datetime))
                  DATE_TRUNC('day', ps.datetime) AS date
                , COALESCE(ps.collateral_token_balance * ps.collateral_token_price, 0)
                  + COALESCE(ps.quote_token_balance * ps.quote_token_price, 0) AS amount
            FROM {pool_snapshot_table} ps
            WHERE ps.datetime >= %s AND ps.address = %s
            ORDER BY 1, ps.datetime DESC
        """.format(
            pool_snapshot_table=self.models.pool_snapshot._meta.db_table,
        )

        data = fetch_all(sql, sql_vars)
        return data

    def _get_pool_size(self, pool_address):
        sql_vars = [self.days_ago_dt, pool_address]
        sql = """
            SELECT DISTINCT ON (DATE_TRUNC('day', ps.datetime))
                  DATE_TRUNC('day', ps.datetime) AS date
                , ps.pool_size AS amount
            FROM {pool_snapshot_table} ps
            WHERE ps.datetime >= %s AND ps.address = %s
            ORDER BY 1, ps.datetime DESC
        """.format(
            pool_snapshot_table=self.models.pool_snapshot._meta.db_table,
        )

        data = fetch_all(sql, sql_vars)
        return data

    def _get_debt(self, pool_address):
        sql_vars = [self.days_ago_dt, pool_address]
        sql = """
            SELECT DISTINCT ON (DATE_TRUNC('day', ps.datetime))
                  DATE_TRUNC('day', ps.datetime) AS date
                , ps.debt AS amount
            FROM {pool_snapshot_table} ps
            WHERE ps.datetime >= %s AND ps.address = %s
            ORDER BY 1, ps.datetime DESC
        """.format(
            pool_snapshot_table=self.models.pool_snapshot._meta.db_table,
        )

        data = fetch_all(sql, sql_vars)
        return data

    def _get_pledged_collateral(self, pool_address):
        sql_vars = [self.days_ago_dt, pool_address]
        sql = """
            SELECT DISTINCT ON (DATE_TRUNC('day', ps.datetime))
                  DATE_TRUNC('day', ps.datetime) AS date
                , ps.pledged_collateral AS amount
            FROM {pool_snapshot_table} ps
            WHERE ps.datetime >= %s AND ps.address = %s
            ORDER BY 1, ps.datetime DESC
        """.format(
            pool_snapshot_table=self.models.pool_snapshot._meta.db_table,
        )

        data = fetch_all(sql, sql_vars)
        return data

    def _get_collateral(self, pool_address):
        sql_vars = [self.days_ago_dt, pool_address]
        sql = """
            SELECT DISTINCT ON (DATE_TRUNC('day', ps.datetime))
                  DATE_TRUNC('day', ps.datetime) AS date
                , ps.collateral_token_balance AS amount
            FROM {pool_snapshot_table} ps
            WHERE ps.datetime >= %s AND ps.address = %s
            ORDER BY 1, ps.datetime DESC
        """.format(
            pool_snapshot_table=self.models.pool_snapshot._meta.db_table,
        )

        data = fetch_all(sql, sql_vars)
        return data

    def _get_volume(self, pool_address):
        sql_vars = [self.days_ago_dt.date(), pool_address]
        sql = """
            SELECT
                  pvs.date
                , pvs.amount
            FROM {pool_volume_snapshot_table} pvs
            WHERE pvs.date >= %s AND pvs.pool_address = %s
            ORDER BY 1, pvs.date DESC
        """.format(
            pool_volume_snapshot_table=self.models.pool_volume_snapshot._meta.db_table,
        )

        data = fetch_all(sql, sql_vars)

        volume = self.models.pool.objects.get(address=pool_address).volume_today

        data.append(
            {
                "date": datetime.now().date(),
                "amount": volume,
            }
        )
        return data

    def _get_apr(self, pool_address):
        if self.days_ago == 30:
            trunc = "hour"
        else:
            trunc = "day"

        sql_vars = [self.days_ago_dt, pool_address]
        sql = """
            SELECT DISTINCT ON (DATE_TRUNC('{date_trunc}', ps.datetime))
                  DATE_TRUNC('{date_trunc}', ps.datetime) AS date
                , ps.lend_rate AS lend_rate
                , ps.borrow_rate AS borrow_rate
            FROM {pool_snapshot_table} ps
            WHERE ps.datetime >= %s AND ps.address = %s
            ORDER BY 1, ps.datetime DESC
        """.format(
            pool_snapshot_table=self.models.pool_snapshot._meta.db_table,
            date_trunc=trunc,
        )

        data = fetch_all(sql, sql_vars)
        return data

    def _get_mau_tu(self, pool_address):
        if self.days_ago == 30:
            trunc = "hour"
        else:
            trunc = "day"

        sql_vars = [self.days_ago_dt, pool_address]
        sql = """
            SELECT DISTINCT ON (DATE_TRUNC('{date_trunc}', ps.datetime))
                  DATE_TRUNC('{date_trunc}', ps.datetime) AS date
                , ps.actual_utilization
                , ps.target_utilization
                , -ps.target_utilization - 1 + sqrt(8 * ps.target_utilization + 1)
                AS actual_utilization_upper_bound
                , CASE WHEN 9 - 8 * 1.02 * ps.target_utilization >= 0
                    THEN -1.02 * ps.target_utilization + 3 - sqrt(
                        9 - 8 * 1.02 * ps.target_utilization)
                    ELSE 0
                  END AS actual_utilization_lower_bound
            FROM {pool_snapshot_table} ps
            WHERE ps.datetime >= %s AND ps.address = %s
            ORDER BY 1, ps.datetime DESC
        """.format(
            pool_snapshot_table=self.models.pool_snapshot._meta.db_table,
            date_trunc=trunc,
        )

        data = fetch_all(sql, sql_vars)
        return data

    def _get_burn(self, pool_address):
        sql_vars = [pool_address]
        sql = """
            SELECT
                  rat.block_datetime AS date
                , SUM(rat.ajna_burned) OVER (
                    PARTITION BY rat.pool_address ORDER BY rat.block_datetime)
                    AS cumulative_ajna_burned
                , SUM(rat.ajna_burned * rat.ajna_price) OVER (
                    PARTITION BY rat.pool_address ORDER BY rat.block_datetime)
                    AS cumulative_ajna_burned_usd
            FROM {reserve_auction_take_table} rat
            WHERE rat.pool_address = %s
            ORDER BY rat.block_datetime
        """.format(
            reserve_auction_take_table=self.models.reserve_auction_take._meta.db_table,
        )

        data = fetch_all(sql, sql_vars)

        if data:
            current = deepcopy(data[-1])
            current["date"] = datetime.now()
            data.append(current)
        return data

    def get(self, request, pool_address, historic_type):
        data = None
        match historic_type:
            case "tvl":
                data = self._get_tvl(pool_address)
            case "pool_size":
                data = self._get_pool_size(pool_address)
            case "debt":
                data = self._get_debt(pool_address)
            case "pledged_collateral":
                data = self._get_pledged_collateral(pool_address)
            case "collateral":
                data = self._get_collateral(pool_address)
            case "volume":
                data = self._get_volume(pool_address)
            case "apr":
                data = self._get_apr(pool_address)
            case "mau_tu":
                data = self._get_mau_tu(pool_address)
            case "burn":
                data = self._get_burn(pool_address)

            case _:
                raise Http404

        return Response(data, status.HTTP_200_OK)


class PoolEventsView(RawSQLPaginatedChainView):
    order_nulls_last = True
    default_order = "-order_index"
    ordering_fields = ["order_index"]

    def get_raw_sql(self, pool_address, query_params, **kwargs):
        event_name = query_params.get("name")
        sql = """
            SELECT
                  wallet_addresses
                , pool_address
                , block_number
                , block_datetime
                , order_index
                , transaction_hash
                , name
                , data
            FROM {pool_event_table}
            WHERE pool_address = %s
        """.format(pool_event_table=self.models.pool_event._meta.db_table)

        if event_name:
            sql = "{} AND name = %s".format(sql)
            sql_vars = [pool_address, event_name]
        else:
            sql_vars = [pool_address]

        return sql, sql_vars

    def get_additional_data(self, data, pool_address, **kwargs):
        sql = """
            SELECT
                  pool.address
                , pool.collateral_token_symbol
                , pool.collateral_token_address
                , pool.quote_token_symbol
                , pool.quote_token_address
            FROM {pool_table} AS pool
            WHERE pool.address = %s
        """.format(
            pool_table=self.models.pool._meta.db_table,
        )

        pool_data = fetch_one(sql, [pool_address])

        if not pool_data:
            raise Http404

        return pool_data

    def serialize_data(self, data):
        for row in data:
            row["data"] = parse_event_data(row, self.chain)
        return data


class PoolPositionsView(RawSQLPaginatedChainView):
    days_ago_required = False
    days_ago_default = 1
    days_ago_options = [1, 7, 30, 90, 365, 9999]
    order_nulls_last = True
    search_fields = ["wallet_address"]

    def _get_borrower_sql(self, only_closed):
        if only_closed:
            position_filter = "AND (cwp.t0debt = 0 AND cwp.collateral = 0)"
        else:
            position_filter = "AND (cwp.t0debt > 0 OR cwp.collateral > 0)"

        return """
            WITH previous AS (
                SELECT DISTINCT ON (wp.wallet_address)
                      wp.wallet_address
                    , wp.t0debt
                    , wp.collateral
                FROM {wallet_position_table} wp
                WHERE wp.datetime <= %s AND wp.pool_address = %s
                ORDER BY wp.wallet_address, wp.datetime DESC
            ),
            previous_pool AS (
                SELECT DISTINCT ON (ps.address)
                      ps.address
                    , ps.quote_token_price
                    , ps.collateral_token_price
                    , ps.pending_inflator
                FROM {pool_snapshot_table} ps
                WHERE ps.datetime > (%s - INTERVAL '7 DAY')
                    AND ps.datetime <= %s
                    AND ps.address = %s
                ORDER BY ps.address, ps.datetime DESC
            )

            SELECT
                  x.wallet_address
                , x.collateral
                , x.collateral_usd
                , x.debt
                , x.debt_usd
                , x.collateral_token_symbol
                , x.collateral_token_address
                , x.quote_token_symbol
                , x.quote_token_address
                , x.prev_collateral
                , x.prev_debt
                , x.prev_collateral_usd
                , x.prev_debt_usd
                , x.in_liquidation
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
                , w.last_activity
                , w.first_activity
            FROM (
                SELECT
                      cwp.wallet_address
                    , cwp.in_liquidation
                    , cwp.collateral
                    , cwp.collateral * ct.underlying_price AS collateral_usd
                    , cwp.t0debt * p.pending_inflator AS debt
                    , cwp.t0debt * p.pending_inflator * qt.underlying_price AS debt_usd
                    , ct.symbol AS collateral_token_symbol
                    , ct.underlying_address AS collateral_token_address
                    , qt.symbol AS quote_token_symbol
                    , qt.underlying_address AS quote_token_address
                    , p.t0debt * p.pending_inflator AS pool_debt
                    , p.lup
                    , prev.collateral AS prev_collateral
                    , prev.t0debt * p.pending_inflator AS prev_debt
                    , prev.collateral * prev_pool.collateral_token_price AS prev_collateral_usd
                    , (prev.t0debt * prev_pool.pending_inflator * prev_pool.quote_token_price)
                        AS prev_debt_usd
                FROM {current_wallet_position_table} cwp
                JOIN {pool_table} p
                    ON cwp.pool_address = p.address
                JOIN {token_table} AS ct
                    ON p.collateral_token_address = ct.underlying_address
                JOIN {token_table} AS qt
                    ON p.quote_token_address = qt.underlying_address
                LEFT JOIN previous AS prev
                    ON cwp.wallet_address = prev.wallet_address
                LEFT JOIN previous_pool AS prev_pool
                    ON cwp.pool_address = prev_pool.address
                WHERE cwp.pool_address = %s
                    {position_filter}
            ) x
            LEFT JOIN {wallet_table} w
                ON x.wallet_address = w.address
        """.format(
            current_wallet_position_table=self.models.current_wallet_position._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
            wallet_position_table=self.models.wallet_position._meta.db_table,
            wallet_table=self.models.wallet._meta.db_table,
            pool_snapshot_table=self.models.pool_snapshot._meta.db_table,
            position_filter=position_filter,
        )

    def _get_depositor_sql(self, only_closed):
        if only_closed:
            position_filter = "AND cwp.supply = 0"
        else:
            position_filter = "AND cwp.supply > 0"

        return """
            WITH previous AS (
                SELECT DISTINCT ON (wp.wallet_address)
                      wp.wallet_address
                    , wp.supply
                FROM {wallet_position} wp
                WHERE wp.datetime <= %s AND wp.pool_address = %s
                ORDER BY wp.wallet_address, wp.datetime DESC
            ),
            previous_pool AS (
                SELECT DISTINCT ON (ps.address)
                      ps.address
                    , ps.quote_token_price
                FROM {pool_snapshot_table} ps
                WHERE ps.datetime > (%s - INTERVAL '7 DAY')
                    AND ps.datetime <= %s
                    AND ps.address = %s
                ORDER BY ps.address, ps.datetime DESC
            )

            SELECT
                  cwp.wallet_address
                , cwp.supply
                , cwp.supply * qt.underlying_price AS supply_usd
                , qt.symbol AS quote_token_symbol
                , qt.underlying_address AS quote_token_address
                , prev.supply AS prev_supply
                , prev.supply * prev_pool.quote_token_price  AS prev_supply_usd
                , CASE
                    WHEN NULLIF(cwp.supply, 0) IS NULL
                        OR NULLIF(p.pool_size, 0) IS NULL
                    THEN NULL
                    ELSE cwp.supply / p.pool_size
                  END AS supply_share
                , w.last_activity
                , w.first_activity
            FROM {current_wallet_position_table} cwp
            JOIN {pool_table} p
                ON cwp.pool_address = p.address
            JOIN {token_table} AS qt
                ON p.quote_token_address = qt.underlying_address
            LEFT JOIN previous AS prev
                ON cwp.wallet_address = prev.wallet_address
            LEFT JOIN {wallet_table} w
                ON cwp.wallet_address = w.address
            LEFT JOIN previous_pool AS prev_pool
                    ON cwp.pool_address = prev_pool.address
            WHERE cwp.pool_address = %s
                {position_filter}
        """.format(
            current_wallet_position_table=self.models.current_wallet_position._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
            wallet_position=self.models.wallet_position._meta.db_table,
            wallet_table=self.models.wallet._meta.db_table,
            pool_snapshot_table=self.models.pool_snapshot._meta.db_table,
            position_filter=position_filter,
        )

    def get_raw_sql(self, pool_address, query_params, search_filters, **kwargs):
        wallet_type = query_params.get("type")

        only_closed = query_params.get("closed") == "1"

        if wallet_type == "depositor":
            sql = self._get_depositor_sql(only_closed)
            self.ordering_fields = [
                "supply",
                "last_activity",
                "first_activity",
                "supply_share",
            ]
        else:
            sql = self._get_borrower_sql(only_closed)
            self.ordering_fields = [
                "debt",
                "collateral",
                "health_rate",
                "debt_share",
                "first_activity",
                "last_activity",
            ]

        sql_vars = [
            self.days_ago_dt,
            pool_address,
            self.days_ago_dt,
            self.days_ago_dt,
            pool_address,
            pool_address,
        ]

        filters = []
        if search_filters:
            search_sql, search_vars = search_filters

            filter_op = "WHERE"
            if wallet_type == "depositor":
                filter_op = "AND"
                search_sql = search_sql.replace("wallet_address", "cwp.wallet_address")

            filters.append(search_sql)
            sql_vars.extend(search_vars)

        if filters:
            sql += " {} {}".format(filter_op, " AND ".join(filters))

        return sql, sql_vars

    def get_additional_data(self, data, pool_address, **kwargs):
        sql = """
            SELECT
                  pool.address
                , pool.collateral_token_symbol AS collateral_token_symbol
                , pool.quote_token_symbol AS quote_token_symbol
            FROM {pool_table} AS pool
            WHERE pool.address = %s
        """.format(
            pool_table=self.models.pool._meta.db_table,
        )

        pool_data = fetch_one(sql, [pool_address])

        if not pool_data:
            raise Http404

        return pool_data


class BucketsListView(RawSQLPaginatedChainView):
    order_nulls_last = True
    default_order = "-bucket_price"
    ordering_fields = [
        "bucket_price",
        "collateral",
        "deposit",
        "is_utilized",
        "bucket_index",
    ]
    search_fields = ["bucket_index::text"]

    def get_raw_sql(self, pool_address, search_filters, **kwargs):
        sql_vars = [pool_address]
        sql = """
            SELECT
                  bucket.bucket_index
                , bucket.bucket_price
                , bucket.exchange_rate
                , bucket.pool_address
                , bucket.collateral
                , bucket.deposit
                , bucket.lpb
                , pool.lup
                , bucket.bucket_price >= pool.lup AS is_utilized
                , collateral_token.underlying_price AS collateral_token_underlying_price
                , collateral_token.symbol AS collateral_token_symbol
                , collateral_token.underlying_address AS collateral_token_address
                , quote_token.symbol AS quote_token_symbol
                , quote_token.underlying_price AS quote_token_underlying_price
                , quote_token.underlying_address AS quote_token_address
            FROM {bucket_table} AS bucket
            JOIN {pool_table} AS pool
                ON bucket.pool_address = pool.address
            JOIN {token_table} AS collateral_token
                ON pool.collateral_token_address = collateral_token.underlying_address
            JOIN {token_table} AS quote_token
                ON pool.quote_token_address = quote_token.underlying_address
            WHERE pool_address = %s
                AND (collateral > 0 OR deposit > 0)
        """.format(
            bucket_table=self.models.bucket._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
        )

        filters = []
        if search_filters:
            search_sql, search_vars = search_filters
            filters.append(search_sql)
            sql_vars.extend(search_vars)

        if filters:
            sql += " AND {}".format(" AND ".join(filters))
        return sql, sql_vars

    def get_additional_data(self, data, pool_address, **kwargs):
        sql = """
            SELECT
                  pool.address
                , pool.collateral_token_symbol
                , pool.collateral_token_address
                , pool.quote_token_symbol
                , pool.quote_token_address
            FROM {pool_table} AS pool
            WHERE pool.address = %s
        """.format(
            pool_table=self.models.pool._meta.db_table,
        )

        pool_data = fetch_one(sql, [pool_address])

        if not pool_data:
            raise Http404

        return pool_data


class BucketsGraphView(BaseChainView):
    def get(self, request, pool_address):
        sql_vars = [pool_address]
        sql = """
            SELECT
                  bucket.bucket_index
                , bucket.bucket_price
                , bucket.deposit
                , pool.debt AS total_pool_debt
            FROM {bucket_table} AS bucket
            JOIN {pool_table} AS pool
                ON bucket.pool_address = pool.address
            WHERE bucket.pool_address = %s
                AND bucket.deposit > 0
                AND (bucket.bucket_price > pool.hpb - pool.hpb * 0.3
                    OR bucket.bucket_price > pool.htp - pool.htp * 0.05)
            ORDER BY bucket.bucket_price DESC
        """.format(
            bucket_table=self.models.bucket._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
        )

        buckets = fetch_all(sql, sql_vars)

        data = []
        if not buckets:
            return Response(data, status.HTTP_200_OK)

        remaining_debt = buckets[0]["total_pool_debt"]
        for bucket in buckets:
            deposit = bucket["deposit"]
            if remaining_debt > 0:
                if remaining_debt >= deposit:
                    amount = deposit
                    remaining_debt -= deposit
                    data.append(
                        {
                            "bucket_index": bucket["bucket_index"],
                            "bucket_price": bucket["bucket_price"],
                            "amount": amount,
                            "type": "utilized",
                            "deposit": bucket["deposit"],
                        }
                    )
                else:
                    amount = deposit - remaining_debt
                    data.append(
                        {
                            "bucket_index": bucket["bucket_index"],
                            "bucket_price": bucket["bucket_price"],
                            "amount": remaining_debt,
                            "type": "utilized",
                            "deposit": bucket["deposit"],
                        }
                    )
                    data.append(
                        {
                            "bucket_index": bucket["bucket_index"],
                            "bucket_price": bucket["bucket_price"],
                            "amount": amount,
                            "type": "not_utilized",
                            "deposit": bucket["deposit"],
                        }
                    )
                    remaining_debt = 0
            else:
                data.append(
                    {
                        "bucket_index": bucket["bucket_index"],
                        "bucket_price": bucket["bucket_price"],
                        "amount": deposit,
                        "type": "not_utilized",
                        "deposit": bucket["deposit"],
                    }
                )

        return Response(data, status.HTTP_200_OK)


class BucketView(BaseChainView):
    def get(self, request, pool_address, bucket_index):
        sql = """
            SELECT
                  b.bucket_index
                , b.bucket_price
                , b.exchange_rate
                , b.pool_address
                , b.collateral
                , b.deposit
                , b.lpb
                , pool.lup
                , b.bucket_price >= pool.lup AS is_utilized
                , ct.underlying_price AS collateral_token_underlying_price
                , ct.symbol AS collateral_token_symbol
                , ct.underlying_address AS collateral_token_address
                , qt.symbol AS quote_token_symbol
                , qt.underlying_address AS quote_token_address
                , qt.underlying_price AS quote_token_underlying_price
            FROM {bucket_table} AS b
            JOIN {pool_table} AS pool
                ON b.pool_address = pool.address
            JOIN {token_table} AS ct
                ON pool.collateral_token_address = ct.underlying_address
            JOIN {token_table} AS qt
                ON pool.quote_token_address = qt.underlying_address
            WHERE b.pool_address = %s
                AND b.bucket_index = %s
        """.format(
            bucket_table=self.models.bucket._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
        )

        data = fetch_one(sql, [pool_address, bucket_index])

        if not data:
            raise Http404

        return Response(data, status.HTTP_200_OK)


class BucketHistoricView(BaseChainView):
    def get(self, request, pool_address, bucket_index):
        sql = """
            SELECT
                  bs.bucket_index
                , bs.bucket_price
                , bs.exchange_rate
                , bs.pool_address
                , bs.collateral
                , bs.deposit
                , bs.lpb
                , bs.block_datetime
                , ct.underlying_price AS collateral_token_underlying_price
                , ct.symbol AS collateral_token_symbol
                , qt.symbol AS quote_token_symbol
                , qt.underlying_price AS quote_token_underlying_price
            FROM {bucket_state_table} AS bs
            JOIN {pool_table} AS pool
                ON bs.pool_address = pool.address
            JOIN {token_table} AS ct
                ON pool.collateral_token_address = ct.underlying_address
            JOIN {token_table} AS qt
                ON pool.quote_token_address = qt.underlying_address
            WHERE bs.pool_address = %s
                AND bs.bucket_index = %s
        """.format(
            bucket_state_table=self.models.bucket_state._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
        )

        data = fetch_all(sql, [pool_address, bucket_index])

        if not data:
            raise Http404

        return Response(data, status.HTTP_200_OK)


class BucketDepositorsView(RawSQLPaginatedChainView):
    default_order = "-deposit"
    ordering_fields = [
        "wallet_address",
        "deposit",
    ]

    def get_raw_sql(self, pool_address, bucket_index, **kwargs):
        sql_vars = [pool_address, bucket_index]
        sql = """
            SELECT
                  wallet_address
                , deposit
            FROM (
                SELECT DISTINCT ON (wbs.wallet_address)
                      wbs.wallet_address
                    , wbs.deposit
                FROM {wallet_bucket_state_table} AS wbs
                WHERE wbs.pool_address = %s
                    AND wbs.bucket_index = %s
                ORDER BY 1, wbs.block_number DESC
            ) x
            WHERE deposit > 0
        """.format(
            wallet_bucket_state_table=self.models.wallet_bucket_state._meta.db_table,
        )
        return sql, sql_vars


class BucketEventsView(RawSQLPaginatedChainView):
    default_order = "-order_index"
    ordering_fields = ["order_index"]

    def get_raw_sql(self, pool_address, bucket_index, query_params, **kwargs):
        try:
            bucket_index = int(bucket_index)
        except ValueError:
            raise Http404 from None

        event_name = query_params.get("name")
        sql = """
            SELECT
                  wallet_addresses
                , pool_address
                , block_number
                , block_datetime
                , order_index
                , transaction_hash
                , name
                , data
            FROM {pool_event_table}
            WHERE pool_address = %s
                AND bucket_indexes @> %s
        """.format(pool_event_table=self.models.pool_event._meta.db_table)

        if event_name:
            sql = "{} AND name = %s".format(sql)
            sql_vars = [pool_address, [bucket_index], event_name]
        else:
            sql_vars = [pool_address, [bucket_index]]

        return sql, sql_vars

    def serialize_data(self, data):
        for row in data:
            row["data"] = parse_event_data(row, self.chain)
        return data

    def get_additional_data(self, data, pool_address, **kwargs):
        sql = """
            SELECT
                  pool.address
                , pool.collateral_token_symbol
                , pool.collateral_token_address
                , pool.quote_token_symbol
                , pool.quote_token_address
            FROM {pool_table} AS pool
            WHERE pool.address = %s
        """.format(
            pool_table=self.models.pool._meta.db_table,
        )

        pool_data = fetch_one(sql, [pool_address])

        if not pool_data:
            raise Http404

        return pool_data


class AuctionsSettledView(RawSQLPaginatedChainView):
    default_order = "-settle_time"
    ordering_fields = [
        "collateral",
        "debt",
        "settle_time",
    ]

    def get_raw_sql(self, pool_address, **kwargs):
        sql = """
            SELECT
                  at.uid
                , at.settle_time
                , at.neutral_price
                , at.debt
                , at.collateral
                , at.borrower
                , w.eoa AS borrower_eoa
                , at.debt * ak.quote_token_price AS debt_usd
                , at.collateral * ak.collateral_token_price AS collateral_usd
                , at.pool_address
                , p.collateral_token_symbol
                , p.collateral_token_address
                , p.quote_token_symbol
                , p.quote_token_address
            FROM {auction_table} at
            JOIN {auction_kick_table} ak
                ON at.uid = ak.auction_uid
            JOIN {pool_table} p
                ON at.pool_address = p.address
            LEFT JOIN {wallet_table} w
                on at.borrower = w.address
            WHERE at.settled = TRUE
                AND p.address = %s
        """.format(
            auction_table=self.models.auction._meta.db_table,
            auction_kick_table=self.models.auction_kick._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            wallet_table=self.models.wallet._meta.db_table,
        )
        sql_vars = [pool_address]
        return sql, sql_vars


class AuctionsActiveView(RawSQLPaginatedChainView):
    default_order = "-kick_time"
    ordering_fields = [
        "collateral_remaining",
        "debt",
        "kick_time",
    ]

    def get_raw_sql(self, pool_address, **kwargs):
        sql = """
            SELECT
                  at.uid
                , at.pool_address
                , at.debt_remaining
                , at.debt_remaining * ak.quote_token_price AS debt_remaining_usd
                , at.collateral_remaining
                , at.collateral_remaining * ak.collateral_token_price AS collateral_remaining_usd
                , at.borrower
                , w.eoa AS borrower_eoa
                , w.address
                , p.collateral_token_symbol
                , p.collateral_token_address
                , p.quote_token_symbol
                , p.quote_token_address
                , ak.block_datetime AS kick_time
                , p.lup
                , p.lup * ak.quote_token_price AS lup_usd
            FROM {auction_table} at
            JOIN {auction_kick_table} ak
                ON at.uid = ak.auction_uid
            JOIN {pool_table} p
                ON at.pool_address = p.address
            LEFT JOIN {wallet_table} w
                on at.borrower = w.address
            WHERE at.settled = False
                AND p.address = %s
        """.format(
            auction_table=self.models.auction._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            auction_kick_table=self.models.auction_kick._meta.db_table,
            wallet_table=self.models.wallet._meta.db_table,
        )

        sql_vars = [pool_address]
        return sql, sql_vars


class AuctionsToKickView(RawSQLPaginatedChainView):
    default_order = "-debt"

    def get_raw_sql(self, pool_address, **kwargs):
        at_risk_sql = WALLETS_AT_RISK_SQL.format(
            current_wallet_position_table=self.models.current_wallet_position._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
            wallet_table=self.models.wallet._meta.db_table,
        )
        at_risk_sql = "{} AND x.pool_address = %s".format(at_risk_sql)

        sql = """
            WITH at_risk AS (
                {at_risk_sql}
            ),

            kicked AS (
                SELECT
                      at.uid
                    , at.borrower
                FROM {auction_table} at
                JOIN {auction_kick_table} ak
                    ON at.uid = ak.auction_uid
                WHERE at.settled = False
                    AND at.pool_address = %s
            )

            SELECT
                ar.*
            FROM at_risk ar
            LEFT JOIN kicked k
                ON k.borrower = ar.wallet_address
            WHERE k.borrower IS NULL
        """.format(
            at_risk_sql=at_risk_sql,
            auction_table=self.models.auction._meta.db_table,
            auction_kick_table=self.models.auction_kick._meta.db_table,
        )

        sql_vars = [MAX_INFLATED_PRICE, 0, pool_address, pool_address]

        return sql, sql_vars


class PoolReserveAuctionsActiveView(RawSQLPaginatedChainView):
    default_order = "-kick_datetime"
    ordering_fields = [
        "pool_address",
        "kick_datetime",
        "claimable_reserves_remaining",
        "last_take_price",
        "ajna_burned",
    ]

    def get_raw_sql(self, pool_address, **kwargs):
        sql = """
            SELECT
                  ra.uid
                , ra.pool_address
                , ra.claimable_reserves
                , ra.claimable_reserves_remaining
                , ra.last_take_price
                , ra.burn_epoch
                , ra.ajna_burned
                , rak.block_number
                , rak.block_datetime AS kick_datetime
                , p.collateral_token_symbol
                , p.collateral_token_address
                , p.quote_token_symbol
                , p.quote_token_address
                , 'active' AS type
                , COUNT(rat.order_index) as take_count
            FROM {reserve_auction_table} ra
            JOIN {reserve_auction_kick_table} rak
                ON rak.reserve_auction_uid = ra.uid
            LEFT JOIN {reserve_auction_take_table} rat
                ON rat.reserve_auction_uid = ra.uid
            JOIN {pool_table} p
                ON ra.pool_address = p.address
            WHERE (
                    rak.block_datetime + INTERVAL '72 hours' > CURRENT_TIMESTAMP
                    AND ra.claimable_reserves_remaining > 0
                )
                AND ra.pool_address = %s
            GROUP BY 1,2,3,4,5,6,7,8,9,10,11,12,13,14
        """.format(
            reserve_auction_table=self.models.reserve_auction._meta.db_table,
            reserve_auction_kick_table=self.models.reserve_auction_kick._meta.db_table,
            reserve_auction_take_table=self.models.reserve_auction_take._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
        )
        sql_vars = [pool_address]
        return sql, sql_vars

    def serialize_data(self, data):
        for row in data:
            row["auction_price"] = calculate_current_auction_price(
                row["kick_datetime"], row["claimable_reserves"]
            )
        return data


class PoolReserveAuctionsExpiredView(RawSQLPaginatedChainView):
    default_order = "-block_number"
    ordering_fields = [
        "block_number",
        "pool_address",
        "claimable_reserves",
        "last_take_price",
        "take_count",
        "ajna_burned",
    ]

    def get_raw_sql(self, pool_address, **kwargs):
        sql = """
            SELECT
                  ra.uid
                , ra.pool_address
                , ra.claimable_reserves
                , ra.claimable_reserves_remaining
                , ra.last_take_price
                , ra.burn_epoch
                , ra.ajna_burned
                , rak.block_number
                , rak.transaction_hash
                , rak.block_datetime
                , p.collateral_token_symbol
                , p.collateral_token_address
                , p.quote_token_symbol
                , p.quote_token_address
                , 'expired' AS type
                , COUNT(rat.order_index) as take_count
            FROM {reserve_auction_table} ra
            JOIN {reserve_auction_kick_table} rak
                ON rak.reserve_auction_uid = ra.uid
            LEFT JOIN {reserve_auction_take_table} rat
                ON rat.reserve_auction_uid = ra.uid
            JOIN {pool_table} p
                ON ra.pool_address = p.address
            WHERE (
                    rak.block_datetime + INTERVAL '72 hours' <= CURRENT_TIMESTAMP
                    OR ra.claimable_reserves_remaining = 0
                )
                AND ra.pool_address = %s
            GROUP BY 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
        """.format(
            reserve_auction_table=self.models.reserve_auction._meta.db_table,
            reserve_auction_kick_table=self.models.reserve_auction_kick._meta.db_table,
            reserve_auction_take_table=self.models.reserve_auction_take._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
        )
        sql_vars = [pool_address]
        return sql, sql_vars


class PoolAtRiskView(BaseChainView):
    def get(self, request, pool_address):
        sql = """
            SELECT
                  CASE WHEN w.price_change > 0
                    THEN CEIL(w.price_change * 100)::int
                    ELSE FLOOR(w.price_change * 100)::int
                  END AS change
                , SUM(w.collateral) AS amount
                , SUM(w.collateral_usd) AS amount_usd
            FROM ({}) w
            WHERE w.pool_address = %s
            GROUP BY 1
            ORDER BY 1 DESC
        """.format(
            WALLETS_AT_RISK_SQL.format(
                current_wallet_position_table=self.models.current_wallet_position._meta.db_table,
                pool_table=self.models.pool._meta.db_table,
                token_table=self.models.token._meta.db_table,
                wallet_table=self.models.wallet._meta.db_table,
            )
        )
        sql_vars = [MAX_INFLATED_PRICE, -0.8, pool_address]
        at_risk = fetch_all(sql, sql_vars)
        return Response(at_risk, status.HTTP_200_OK)


class BurnHistoryView(BaseChainView):
    def get(self, request, pool_address):
        sql_vars = [pool_address]
        sql = """
            SELECT
                  rat.block_datetime AS date
                , rat.ajna_burned
                , rat.ajna_burned * rat.ajna_price AS ajna_burned_usd
                , SUM(rat.ajna_burned) OVER (
                    PARTITION BY rat.pool_address ORDER BY rat.block_datetime)
                    AS cumulative_ajna_burned
                , SUM(rat.ajna_burned * rat.ajna_price) OVER (
                    PARTITION BY rat.pool_address ORDER BY rat.block_datetime)
                    AS cumulative_ajna_burned_usd
            FROM {reserve_auction_take_table} rat
            WHERE rat.pool_address = %s
            ORDER BY rat.block_datetime
        """.format(
            reserve_auction_take_table=self.models.reserve_auction_take._meta.db_table,
        )

        data = fetch_all(sql, sql_vars)

        if data:
            current = deepcopy(data[-1])
            current["date"] = datetime.now()
            data.append(current)

        return Response(data, status.HTTP_200_OK)
