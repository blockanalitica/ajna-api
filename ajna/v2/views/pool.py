from django.db import connection
from django.http import Http404
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
