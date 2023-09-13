from datetime import datetime
from decimal import Decimal

from django.db import connection
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response

from ajna.utils.db import fetch_all, fetch_one

from . import BaseChainView, RawSQLPaginatedChainView

POOLS_SQL = """
    WITH previous AS (
        SELECT DISTINCT ON (ps.address)
              ps.address
            , ps.pledged_collateral
            , ps.pool_size
            , ps.t0debt * ps.pending_inflator as debt
            , ps.total_ajna_burned
            , ps.borrow_rate
            , ps.lend_rate
            , ps.pledged_collateral * ps.collateral_token_price AS pledged_collateral_usd
            , ps.pool_size * ps.quote_token_price AS pool_size_usd
            , ps.debt * ps.quote_token_price AS debt_usd
            , (ps.collateral_token_balance * ps.collateral_token_price) +
              (ps.quote_token_balance * ps.quote_token_price) AS tvl
        FROM {pool_snapshot_table} ps
        WHERE ps.datetime <= %s
        ORDER BY ps.address, ps.datetime DESC
    )

    SELECT
          pool.address
        , pool.quote_token_balance
        , pool.collateral_token_balance
        , pool.pledged_collateral
        , pool.pledged_collateral * collateral_token.underlying_price AS pledged_collateral_usd
        , pool.pool_size
        , pool.pool_size * quote_token.underlying_price AS pool_size_usd
        , pool.t0debt * pool.pending_inflator as debt
        , pool.t0debt * pool.pending_inflator * quote_token.underlying_price AS debt_usd
        , pool.borrow_rate
        , pool.lend_rate
        , pool.total_ajna_burned
        , collateral_token.symbol AS collateral_token_symbol
        , collateral_token.name AS collateral_token_name
        , quote_token.symbol AS quote_token_symbol
        , quote_token.name AS quote_token_name
        , COALESCE(
            (pool.collateral_token_balance * collateral_token.underlying_price) +
            (pool.quote_token_balance * quote_token.underlying_price),
            0
          ) AS tvl

        , prev.pledged_collateral AS prev_pledged_collateral
        , prev.pledged_collateral_usd AS prev_pledged_collateral_usd
        , prev.pool_size AS prev_pool_size
        , prev.pool_size_usd AS prev_pool_size_usd
        , prev.debt AS prev_debt
        , prev.debt_usd AS prev_debt_usd
        , prev.total_ajna_burned AS prev_total_ajna_burned
        , prev.borrow_rate AS prev_borrow_rate
        , prev.lend_rate AS prev_lend_rate
        , prev.tvl AS prev_tvl
    FROM {pool_table} AS pool
    JOIN {token_table} AS collateral_token
        ON pool.collateral_token_address = collateral_token.underlying_address
    JOIN {token_table} AS quote_token
        ON pool.quote_token_address = quote_token.underlying_address
    LEFT JOIN previous AS prev
        ON pool.address = prev.address
"""

SQL_TODAYS_VOLUME_FOR_POOL = """
    SELECT
        SUM(
            CASE
                WHEN name = 'AddCollateral' THEN
                    CAST(data->>'amount' AS NUMERIC) / 1e18 * collateral_token_price
                WHEN name = 'RemoveCollateral' THEN
                    CAST(data->>'amount' AS NUMERIC) / 1e18 * collateral_token_price
                WHEN name = 'AddQuoteToken' THEN
                    CAST(data->>'amount' AS NUMERIC) / 1e18 * quote_token_price
                WHEN name = 'RemoveQuoteToken' THEN
                    CAST(data->>'amount' AS NUMERIC) / 1e18 * quote_token_price
                WHEN name = 'DrawDebt' THEN
                    CAST(data->>'amountBorrowed' AS NUMERIC) / 1e18 * quote_token_price +
                    CAST(data->>'collateralPledged' AS NUMERIC) / 1e18 * collateral_token_price
                WHEN name = 'RepayDebt' THEN
                    CAST(data->>'quoteRepaid' AS NUMERIC) / 1e18 * quote_token_price +
                    CAST(data->>'collateralPulled' AS NUMERIC) / 1e18 * collateral_token_price
            END
        ) AS amount
    FROM {pool_event_table}
    WHERE block_datetime >= CURRENT_DATE
        AND pool_address = %s
        AND name IN (
            'AddCollateral',
            'RemoveCollateral',
            'AddQuoteToken',
            'RemoveQuoteToken',
            'DrawDebt',
            'RepayDebt'
        )
"""


class PoolsView(RawSQLPaginatedChainView):
    order_nulls_last = True
    days_ago_required = False
    days_ago_default = 1
    days_ago_options = [1, 7, 30, 365]
    default_order = "-tvl"
    ordering_fields = [
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

    def get_raw_sql(self, search_filters, **kwargs):
        sql = POOLS_SQL.format(
            token_table=self.models.token._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            pool_snapshot_table=self.models.pool_snapshot._meta.db_table,
        )

        sql_vars = [self.days_ago_dt]
        filters = []
        if search_filters:
            search_sql, search_vars = search_filters
            filters.append(search_sql)
            sql_vars.extend(search_vars)

        if filters:
            sql += " WHERE {}".format(" AND ".join(filters))

        return sql, sql_vars


class PoolView(BaseChainView):
    days_ago_required = False
    days_ago_default = 7
    days_ago_options = [1, 7, 30, 365]

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
                        , ps.pool_size
                        , ps.t0debt * ps.pending_inflator as debt
                        , ps.lup
                        , ps.htp
                        , ps.hpb
                        , ps.pledged_collateral * ps.collateral_token_price AS pledged_collateral_usd
                        , ps.pool_size * ps.quote_token_price AS pool_size_usd
                        , ps.t0debt * ps.pending_inflator * ps.quote_token_price AS debt_usd
                        , ps.total_ajna_burned
                        , ps.quote_token_price
                        , ps.collateral_token_price
                        , ps.reserves
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
                , ((pool.pledged_collateral * collateral_token.underlying_price)
                    / NULLIF(
                        (pool.t0debt * pool.pending_inflator * quote_token.underlying_price), 0)
                    ) as collateralization
                , pool.utilization
                , pool.actual_utilization
                , pool.target_utilization
                , pool.quote_token_balance
                , pool.quote_token_balance * quote_token.underlying_price AS quote_token_balance_usd
                , collateral_token.symbol AS collateral_token_symbol
                , collateral_token.name AS collateral_token_name
                , collateral_token.underlying_price AS collateral_token_underlying_price
                , quote_token.symbol AS quote_token_symbol
                , quote_token.name AS quote_token_name
                , quote_token.underlying_price AS quote_token_underlying_price
                , (pool.collateral_token_balance * collateral_token.underlying_price) +
                  (pool.quote_token_balance * quote_token.underlying_price) AS tvl
                , prev.pledged_collateral_usd + (prev.pool_size_usd - prev.debt_usd) AS prev_tvl
                , prev.pledged_collateral AS prev_pledged_collateral
                , prev.pool_size AS prev_pool_size
                , prev.debt as prev_debt
                , prev.pledged_collateral_usd AS prev_pledged_collateral_usd
                , prev.pool_size_usd AS prev_pool_size_usd
                , prev.debt_usd as prev_debt_usd
                , prev.lup as prev_lup
                , prev.htp as prev_htp
                , prev.hpb as prev_hpb
                , prev.total_ajna_burned as prev_total_ajna_burned
                , prev.quote_token_price as prev_quote_token_price
                , prev.collateral_token_price as prev_collateral_token_price
                , prev.reserves as prev_reserves
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
        with connection.cursor() as cursor:
            cursor.execute(sql, sql_vars)
            pool_data = fetch_one(cursor)

        if not pool_data:
            raise Http404

        # Get todays volume on the fly
        today_sql = SQL_TODAYS_VOLUME_FOR_POOL.format(
            pool_event_table=self.models.pool_event._meta.db_table
        )

        with connection.cursor() as cursor:
            cursor.execute(today_sql, [pool_address])
            today_volume = fetch_one(cursor)
        pool_data["volume"] = today_volume["amount"]

        return Response({"results": pool_data}, status.HTTP_200_OK)


class BucketsView(RawSQLPaginatedChainView):
    order_nulls_last = True
    default_order = "-bucket_price"
    ordering_fields = [
        "bucket_price",
        "collateral",
        "deposit",
        "is_utilized",
        "bucket_index",
    ]

    def get_raw_sql(self, pool_address, search_filters, query_params, **kwargs):
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
                    , quote_token.symbol AS quote_token_symbol
                    , quote_token.underlying_price AS quote_token_underlying_price
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
        return sql, sql_vars


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
            JOIN {token_table} AS collateral_token
                ON pool.collateral_token_address = collateral_token.underlying_address
            JOIN {token_table} AS quote_token
                ON pool.quote_token_address = quote_token.underlying_address
            WHERE bucket.pool_address = %s
                AND bucket.deposit > 0
                AND (bucket.bucket_price > pool.hpb - pool.hpb * 0.3
                    OR bucket.bucket_price > pool.htp - pool.htp * 0.05)
            ORDER BY bucket.bucket_price DESC
        """.format(
            bucket_table=self.models.bucket._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
        )

        with connection.cursor() as cursor:
            cursor.execute(sql, sql_vars)
            buckets = fetch_all(cursor)

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


class PoolHistoricView(BaseChainView):
    """
    A view for retrieving historic information about a specific pool.
    """

    days_ago_required = False
    days_ago_default = 7
    days_ago_options = [30, 365]

    def _get_tvl(self, pool_address):
        sql_vars = [self.days_ago_dt, pool_address]
        sql = """
            SELECT DISTINCT ON (DATE_TRUNC('day', ps.datetime))
                  DATE_TRUNC('day', ps.datetime) AS date
                , (ps.collateral_token_balance * ps.collateral_token_price)
                  + (quote_token_balance * ps.quote_token_price) AS amount
            FROM {pool_snapshot_table} ps
            WHERE ps.datetime >= %s AND ps.address = %s
            ORDER BY 1, ps.datetime DESC
        """.format(
            pool_snapshot_table=self.models.pool_snapshot._meta.db_table,
        )
        with connection.cursor() as cursor:
            cursor.execute(sql, sql_vars)
            data = fetch_all(cursor)
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
        with connection.cursor() as cursor:
            cursor.execute(sql, sql_vars)
            data = fetch_all(cursor)
        return data

    def _get_debt(self, pool_address):
        sql_vars = [self.days_ago_dt, pool_address]
        sql = """
            SELECT DISTINCT ON (DATE_TRUNC('day', ps.datetime))
                  DATE_TRUNC('day', ps.datetime) AS date
                , ps.t0debt * ps.pending_inflator AS amount
            FROM {pool_snapshot_table} ps
            WHERE ps.datetime >= %s AND ps.address = %s
            ORDER BY 1, ps.datetime DESC
        """.format(
            pool_snapshot_table=self.models.pool_snapshot._meta.db_table,
        )
        with connection.cursor() as cursor:
            cursor.execute(sql, sql_vars)
            data = fetch_all(cursor)
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
        with connection.cursor() as cursor:
            cursor.execute(sql, sql_vars)
            data = fetch_all(cursor)
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
        with connection.cursor() as cursor:
            cursor.execute(sql, sql_vars)
            data = fetch_all(cursor)

        # Get todays volume on the fly
        today_sql = SQL_TODAYS_VOLUME_FOR_POOL.format(
            pool_event_table=self.models.pool_event._meta.db_table
        )

        with connection.cursor() as cursor:
            cursor.execute(today_sql, [pool_address])
            today_data = fetch_one(cursor)

        data.append(
            {
                "date": datetime.now().date(),
                "amount": today_data["amount"] or Decimal("0"),
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
        with connection.cursor() as cursor:
            cursor.execute(sql, sql_vars)
            data = fetch_all(cursor)
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
                , -1.02 * ps.target_utilization + 3 - sqrt(9 - 8 * 1.02 * ps.target_utilization)
                AS actual_utilization_lower_bound
            FROM {pool_snapshot_table} ps
            WHERE ps.datetime >= %s AND ps.address = %s
            ORDER BY 1, ps.datetime DESC
        """.format(
            pool_snapshot_table=self.models.pool_snapshot._meta.db_table,
            date_trunc=trunc,
        )
        with connection.cursor() as cursor:
            cursor.execute(sql, sql_vars)
            data = fetch_all(cursor)
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
            case "volume":
                data = self._get_volume(pool_address)
            case "apr":
                data = self._get_apr(pool_address)
            case "mau_tu":
                data = self._get_mau_tu(pool_address)
            case _:
                raise Http404

        return Response(data, status.HTTP_200_OK)


class PoolEventsView(RawSQLPaginatedChainView):
    order_nulls_last = True
    # default_order = "-block_timestamp"
    # ordering_fields = ["block_timestamp", "amount", "collateral", "account"]

    def get_raw_sql(self, search_filters, query_params, **kwargs):
        pool_address = kwargs["pool_address"]
        event_name = query_params.get("name")
        sql = """
            SELECT
                  pool.address
                , collateral_token.symbol AS collateral_token_symbol
                , quote_token.symbol AS quote_token_symbol
            FROM {pool_table} AS pool
            JOIN {token_table} AS collateral_token
                ON pool.collateral_token_address = collateral_token.underlying_address
            JOIN {token_table} AS quote_token
                ON pool.quote_token_address = quote_token.underlying_address
            WHERE pool.address = %s
        """.format(
            token_table=self.models.token._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
        )
        with connection.cursor() as cursor:
            cursor.execute(sql, [pool_address])
            pool_data = fetch_one(cursor)

        if not pool_data:
            raise Http404

        sql = """
            SELECT
                *
            FROM {pool_event_table}
            WHERE pool_address = %s
        """.format(
            pool_event_table=self.models.pool_event._meta.db_table
        )

        if event_name:
            sql = "{} AND name = %s".format(sql)
            sql_vars = [pool_address, event_name]
        else:
            sql_vars = [pool_address]

        return sql, sql_vars
