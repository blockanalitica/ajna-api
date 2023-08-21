import csv
from datetime import datetime, timedelta
from decimal import Decimal

from django.db import connection
from django.http import Http404, HttpResponse
from rest_framework import status
from rest_framework.response import Response

from ajna.utils.db import fetch_all, fetch_one

from . import BaseChainView, RawSQLPaginatedChainView

SQL_TODAYS_VOLUME_FOR_POOL = """
    SELECT
        SUM(amount) AS amount
    FROM (
        SELECT amount * price AS amount
        FROM {add_collateral_table}
        WHERE block_timestamp >= EXTRACT(EPOCH FROM CURRENT_DATE) AND pool_address = %s
        UNION ALL
        SELECT amount * price AS amount
        FROM {remove_collateral_table}
        WHERE block_timestamp >= EXTRACT(EPOCH FROM CURRENT_DATE) AND pool_address = %s
        UNION ALL
        SELECT amount * price AS amount
        FROM {add_quote_token_table}
        WHERE block_timestamp >= EXTRACT(EPOCH FROM CURRENT_DATE) AND pool_address = %s
        UNION ALL
        SELECT amount * price AS amount
        FROM {remove_quote_token_table}
        WHERE block_timestamp >= EXTRACT(EPOCH FROM CURRENT_DATE) AND pool_address = %s
        UNION ALL
        SELECT (amount_borrowed * quote_token_price
               + collateral_pledged * collateral_token_price) AS amount
        FROM {draw_debt_table}
        WHERE block_timestamp >= EXTRACT(EPOCH FROM CURRENT_DATE) AND pool_address = %s
        UNION ALL
        SELECT (quote_repaid * quote_token_price
               + collateral_pulled * collateral_token_price) AS amount
        FROM {repay_debt_table}
        WHERE block_timestamp >= EXTRACT(EPOCH FROM CURRENT_DATE) AND pool_address = %s
    ) AS subquery
"""


class PoolView(BaseChainView):
    """
    A view for retrieving information about a specific pool.

    This view accepts a pool address as a parameter and returns pool data along with related
    collateral and quote token information. It uses raw SQL to efficiently fetch the data from
    the database.

    Attributes:
        days_ago_required (bool): Flag indicating if the `days_ago` parameter is required.
        days_ago_default (int): Default value for the `days_ago` parameter.
        days_ago_options (list): List of allowed values for the `days_ago` parameter.

    """

    days_ago_required = False
    days_ago_default = 7
    days_ago_options = [1, 7, 30, 365]

    def get(self, request, pool_address):
        sql_vars = [
            self.days_ago_dt,
            pool_address,
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
                ),
                fee AS (
                    SELECT pool_address, SUM(fee) AS total_fees
                    FROM {draw_debt_table}
                    WHERE pool_address = %s
                    GROUP BY pool_address
                    )
            SELECT
                  pool.address
                , pool.t0debt * pool.pending_inflator as debt
                , pool.quote_token_address
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
                , f.total_fees AS fees
            FROM {pool_table} AS pool
            JOIN {token_table} AS collateral_token
                ON pool.collateral_token_address = collateral_token.underlying_address
            JOIN {token_table} AS quote_token
                ON pool.quote_token_address = quote_token.underlying_address
            LEFT JOIN previous AS prev
                ON pool.address = prev.address
            LEFT JOIN fee AS f
                ON pool.address = f.pool_address
            WHERE pool.address = %s
        """.format(
            token_table=self.models.token._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            pool_snapshot_table=self.models.pool_snapshot._meta.db_table,
            draw_debt_table=self.models.draw_debt._meta.db_table,
        )
        with connection.cursor() as cursor:
            cursor.execute(sql, sql_vars)
            pool_data = fetch_one(cursor)

        if not pool_data:
            raise Http404

        # Get todays volume on the fly
        today_sql = SQL_TODAYS_VOLUME_FOR_POOL.format(
            add_collateral_table=self.models.add_collateral._meta.db_table,
            remove_collateral_table=self.models.remove_collateral._meta.db_table,
            add_quote_token_table=self.models.add_quote_token._meta.db_table,
            remove_quote_token_table=self.models.remove_quote_token._meta.db_table,
            draw_debt_table=self.models.draw_debt._meta.db_table,
            repay_debt_table=self.models.repay_debt._meta.db_table,
        )

        with connection.cursor() as cursor:
            cursor.execute(today_sql, [pool_address] * 6)
            today_volume = fetch_one(cursor)
        pool_data["volume"] = today_volume["amount"]

        return Response({"results": pool_data}, status.HTTP_200_OK)


class BucketsView(RawSQLPaginatedChainView):
    """
    A view for listing all buckets associated with a specific pool address.

    This view accepts a pool address as a parameter and returns a list of
    buckets related to that pool. It uses raw SQL to fetch the bucket data
    from the database, ensuring optimal performance. The resulting list of
    buckets is returned as a JSON response with a 200 status code (OK).
    """

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
            add_collateral_table=self.models.add_collateral._meta.db_table,
            remove_collateral_table=self.models.remove_collateral._meta.db_table,
            add_quote_token_table=self.models.add_quote_token._meta.db_table,
            remove_quote_token_table=self.models.remove_quote_token._meta.db_table,
            draw_debt_table=self.models.draw_debt._meta.db_table,
            repay_debt_table=self.models.repay_debt._meta.db_table,
        )

        with connection.cursor() as cursor:
            cursor.execute(today_sql, [pool_address] * 6)
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
    default_order = "-block_timestamp"
    ordering_fields = ["block_timestamp", "amount", "collateral", "account"]

    def _get_sql_add_collateral(self, pool_data):
        return """
            SELECT
                CONCAT('add_collateral', id) AS id
                , 'add_collateral' AS event_type
                , amount
                , '{collateral_symbol}' AS amount_symbol
                , CAST(NULL AS numeric) AS collateral
                , NULL AS collateral_symbol
                , actor AS account
                , block_number
                , block_timestamp
                , transaction_hash
                , CAST(NULL AS numeric) AS bucket_index_from
                , CAST(NULL AS numeric) AS bucket_index_to
            FROM {add_collateral_table}
            WHERE pool_address = %s AND block_timestamp >= %s
        """.format(
            add_collateral_table=self.models.add_collateral._meta.db_table,
            collateral_symbol=pool_data["collateral_token_symbol"],
        )

    def _get_sql_remove_collateral(self, pool_data):
        return """
            SELECT
                CONCAT('remove_collateral', id) AS id
                , 'remove_collateral' AS event_type
                , amount
                , '{collateral_symbol}' AS amount_symbol
                , CAST(NULL AS numeric) AS collateral
                , NULL AS collateral_symbol
                , claimer AS account
                , block_number
                , block_timestamp
                , transaction_hash
                , CAST(NULL AS numeric) AS bucket_index_from
                , CAST(NULL AS numeric) AS bucket_index_to
            FROM {remove_collateral_table}
            WHERE pool_address = %s AND block_timestamp >= %s
        """.format(
            remove_collateral_table=self.models.remove_collateral._meta.db_table,
            collateral_symbol=pool_data["collateral_token_symbol"],
        )

    def _get_sql_add_quote_token(self, pool_data):
        return """
            SELECT
                CONCAT('add_quote_token', id) AS id
                , 'add_quote_token' AS event_type
                , amount
                , '{quote_symbol}' AS amount_symbol
                , CAST(NULL AS numeric) AS collateral
                , NULL AS collateral_symbol
                , lender AS account
                , block_number
                , block_timestamp
                , transaction_hash
                , CAST(NULL AS numeric) AS bucket_index_from
                , CAST(NULL AS numeric) AS bucket_index_to
            FROM {add_quote_token_table}
            WHERE pool_address = %s AND block_timestamp >= %s
        """.format(
            add_quote_token_table=self.models.add_quote_token._meta.db_table,
            quote_symbol=pool_data["quote_token_symbol"],
        )

    def _get_sql_remove_quote_token(self, pool_data):
        return """
            SELECT
                CONCAT('remove_quote_token', id) AS id
                , 'remove_quote_token' AS event_type
                , amount
                , '{quote_symbol}' AS amount_symbol
                , CAST(NULL AS numeric) AS collateral
                , NULL AS collateral_symbol
                , lender AS account
                , block_number
                , block_timestamp
                , transaction_hash
                , CAST(NULL AS numeric) AS bucket_index_from
                , CAST(NULL AS numeric) AS bucket_index_to
            FROM {remove_quote_token_table}
            WHERE pool_address = %s AND block_timestamp >= %s
        """.format(
            remove_quote_token_table=self.models.remove_quote_token._meta.db_table,
            quote_symbol=pool_data["quote_token_symbol"],
        )

    def _get_sql_move_quote_token(self, pool_data):
        return """
            SELECT
                CONCAT('move_quote_token', id) AS id
                , 'move_quote_token' AS event_type
                , amount
                , '{quote_symbol}' AS amount_symbol
                , CAST(NULL AS numeric) AS collateral
                , NULL AS collateral_symbol
                , lender AS account
                , block_number
                , block_timestamp
                , transaction_hash
                , bucket_index_from
                , bucket_index_to
            FROM {remove_quote_token_table}
            WHERE pool_address = %s AND block_timestamp >= %s
        """.format(
            remove_quote_token_table=self.models.move_quote_token._meta.db_table,
            quote_symbol=pool_data["quote_token_symbol"],
        )

    def _get_sql_draw_debt(self, pool_data):
        return """
            SELECT
                CONCAT('draw_debt', id) AS id
                , 'draw_debt' AS event_type
                , amount_borrowed AS amount
                , '{quote_symbol}' AS amount_symbol
                , collateral_pledged AS collateral
                , '{collateral_symbol}' AS collateral_symbol
                , borrower AS account
                , block_number
                , block_timestamp
                , transaction_hash
                , CAST(NULL AS numeric) AS bucket_index_from
                , CAST(NULL AS numeric) AS bucket_index_to
            FROM {draw_debt_table}
            WHERE pool_address = %s AND block_timestamp >= %s
        """.format(
            draw_debt_table=self.models.draw_debt._meta.db_table,
            quote_symbol=pool_data["quote_token_symbol"],
            collateral_symbol=pool_data["collateral_token_symbol"],
        )

    def _get_sql_repay_debt(self, pool_data):
        return """
            SELECT
                CONCAT('repay_debt', id) AS id
                , 'repay_debt' AS event_type
                , quote_repaid AS amount
                , '{quote_symbol}' AS amount_symbol
                , collateral_pulled AS collateral
                , '{collateral_symbol}' AS collateral_symbol
                , borrower AS account
                , block_number
                , block_timestamp
                , transaction_hash
                , CAST(NULL AS numeric) AS bucket_index_from
                , CAST(NULL AS numeric) AS bucket_index_to
            FROM {repay_debt_table}
            WHERE pool_address = %s AND block_timestamp >= %s
        """.format(
            repay_debt_table=self.models.repay_debt._meta.db_table,
            quote_symbol=pool_data["quote_token_symbol"],
            collateral_symbol=pool_data["collateral_token_symbol"],
        )

    def get_raw_sql(self, search_filters, query_params, **kwargs):
        pool_address = kwargs["pool_address"]
        event_type = query_params.get("type")
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

        # TODO: change this to a reasonable number (perhaps 1 day or something like that)
        timestamp = (datetime.now() - timedelta(days=365)).timestamp()

        sql_vars = [pool_address, timestamp]

        match event_type:
            case "add_collateral":
                sql = self._get_sql_add_collateral(pool_data)
            case "remove_collateral":
                sql = self._get_sql_remove_collateral(pool_data)
            case "add_quote_token":
                sql = self._get_sql_add_quote_token(pool_data)
            case "move_quote_token":
                sql = self._get_sql_move_quote_token(pool_data)
            case "remove_quote_token":
                sql = self._get_sql_remove_quote_token(pool_data)
            case "draw_debt":
                sql = self._get_sql_draw_debt(pool_data)
            case "repay_debt":
                sql = self._get_sql_repay_debt(pool_data)
            case _:
                sql = " UNION ".join(
                    [
                        self._get_sql_add_collateral(pool_data),
                        self._get_sql_remove_collateral(pool_data),
                        self._get_sql_add_quote_token(pool_data),
                        self._get_sql_move_quote_token(pool_data),
                        self._get_sql_remove_quote_token(pool_data),
                        self._get_sql_draw_debt(pool_data),
                        self._get_sql_repay_debt(pool_data),
                    ]
                )
                sql_vars = [pool_address, timestamp] * 7

        return sql, sql_vars


BORROWERS_SQL = """
    SELECT
          y.borrower
        , y.debt AS debt
        , y.debt * quote_token.underlying_price AS debt_usd
        , y.collateral
        , y.collateral * collateral_token.underlying_price AS collateral_usd
        , collateral_token.symbol AS collateral_token_symbol
        , quote_token.symbol AS quote_token_symbol
        , (y.collateral * pool.lup) / NULLIF(y.debt, 0) as health_rate
    FROM (
        SELECT
              x.borrower
            , x.pool_address
            , SUM(x.debt) AS debt
            , SUM(x.collateral) AS collateral
        FROM (
            SELECT
                 dd.borrower
               , dd.pool_address
               , dd.amount_borrowed AS debt
               , dd.collateral_pledged AS collateral
            FROM {draw_debt_table} AS dd
            WHERE dd.pool_address = %s

            UNION

            SELECT
                  rd.borrower
                , rd.pool_address
                , rd.quote_repaid * -1 AS debt
                , rd.collateral_pulled * -1 AS collateral
            FROM {repay_debt_table} rd
            WHERE pool_address = %s
        ) x
        GROUP BY 1, 2
    ) y
    JOIN {pool_table} pool
        ON pool.address = y.pool_address
    JOIN {token_table} AS collateral_token
        ON pool.collateral_token_address = collateral_token.underlying_address
    JOIN {token_table} AS quote_token
        ON pool.quote_token_address = quote_token.underlying_address
"""


class PoolBorrowersView(RawSQLPaginatedChainView):
    order_nulls_last = True
    default_order = "-debt"
    ordering_fields = [
        "debt",
        "collateral",
        "health_rate",
    ]

    def get_raw_sql(self, pool_address, search_filters, query_params, **kwargs):
        sql_vars = [pool_address, pool_address]
        sql = BORROWERS_SQL.format(
            draw_debt_table=self.models.draw_debt._meta.db_table,
            repay_debt_table=self.models.repay_debt._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
        )
        return sql, sql_vars


class PoolBorrowersCsvView(BaseChainView):
    def get(self, request, pool_address):
        sql_vars = [pool_address, pool_address]
        sql = BORROWERS_SQL.format(
            draw_debt_table=self.models.draw_debt._meta.db_table,
            repay_debt_table=self.models.repay_debt._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
        )

        with connection.cursor() as cursor:
            cursor.execute(sql, sql_vars)
            borrowers = fetch_all(cursor)

        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="borrowers.csv"'},
        )
        fieldnames = [
            "borrower",
            "collateral",
            "collateral_usd",
            "collateral_token_symbol",
            "debt",
            "debt_usd",
            "quote_token_symbol",
            "health_rate",
        ]
        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(borrowers)
        return response


LENDERS_SQL = """
    SELECT
          y.lender
        , y.bucket_index
        , y.amount
        , y.amount * quote_token.underlying_price AS amount_usd
        , quote_token.symbol AS token_symbol
        , bucket.bucket_price
    FROM (
        SELECT
              x.lender
            , x.bucket_index
            , x.pool_address
            , SUM(x.amount) AS amount
        FROM (
            SELECT
                  aqt.lender
                , aqt.bucket_index
                , aqt.pool_address
                , aqt.amount
            FROM {add_quote_token_table} AS aqt
            WHERE aqt.pool_address = %s

            UNION

            SELECT
                  rqt.lender
                , rqt.bucket_index
                , rqt.pool_address
                , rqt.amount * -1 AS collateral
            FROM {remove_quote_token_table} rqt
            WHERE rqt.pool_address = %s
        ) x
        GROUP BY 1, 2, 3
    ) y
    JOIN {pool_table} pool
        ON pool.address = y.pool_address
    JOIN {token_table} AS quote_token
        ON pool.quote_token_address = quote_token.underlying_address
    JOIN {bucket_table} AS bucket
        ON bucket.bucket_index = y.bucket_index
        AND bucket.pool_address = y.pool_address
"""


class PoolLendersView(RawSQLPaginatedChainView):
    order_nulls_last = True
    default_order = "-bucket_price"
    ordering_fields = [
        "lender",
        "bucket_index",
        "bucket_price",
        "amount",
        "amount_usd",
    ]

    def get_raw_sql(self, pool_address, search_filters, query_params, **kwargs):
        sql_vars = [pool_address, pool_address]
        sql = LENDERS_SQL.format(
            add_quote_token_table=self.models.add_quote_token._meta.db_table,
            remove_quote_token_table=self.models.remove_quote_token._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
            bucket_table=self.models.bucket._meta.db_table,
        )
        return sql, sql_vars


class PoolLendersCsvView(BaseChainView):
    def get(self, request, pool_address):
        sql_vars = [pool_address, pool_address]
        sql = LENDERS_SQL.format(
            add_quote_token_table=self.models.add_quote_token._meta.db_table,
            remove_quote_token_table=self.models.remove_quote_token._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
            bucket_table=self.models.bucket._meta.db_table,
        )

        with connection.cursor() as cursor:
            cursor.execute(sql, sql_vars)
            borrowers = fetch_all(cursor)

        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="lenders.csv"'},
        )
        fieldnames = [
            "lender",
            "bucket_index",
            "bucket_price",
            "amount",
            "amount_usd",
            "token_symbol",
        ]
        writer = csv.DictWriter(response, fieldnames=fieldnames, dialect="unix")
        writer.writeheader()
        writer.writerows(borrowers)
        return response
