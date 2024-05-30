from django.http import Http404
from rest_framework import status
from rest_framework.response import Response

from ajna.utils.db import fetch_one
from ajna.utils.views import BaseChainView, RawSQLPaginatedChainView

from .pools import POOLS_SQL


class TokensView(RawSQLPaginatedChainView):
    order_nulls_last = True
    days_ago_required = False
    days_ago_default = 1
    days_ago_options = [1, 7, 30, 90, 365, 9999]
    default_order = "-tvl"
    ordering_fields = [
        "symbol",
        "name",
        "pool_count",
        "collateral_amount",
        "quote_amount",
        "tvl",
        "underlying_price",
    ]
    search_fields = ["sub.symbol", "sub.name"]

    def get_raw_sql(self, search_filters, **kwargs):
        sql = """
            WITH previous AS (
                SELECT
                      sub.underlying_address
                    , sub.pool_count
                    , sub.collateral_amount
                    , sub.lended_amount
                    , sub.borrowed_amount
                    , pf.price AS underlying_price
                FROM (
                    SELECT
                          token.underlying_address
                        , COUNT(pool.address) AS pool_count
                        , SUM(
                            CASE WHEN token.underlying_address = pool.collateral_token_address
                                THEN pool.collateral_token_balance
                                ELSE 0
                            END
                          ) AS collateral_amount
                        , SUM(
                            CASE WHEN token.underlying_address = pool.quote_token_address
                            THEN pool.pool_size
                            ELSE 0
                            END) AS lended_amount
                        , SUM(
                            CASE WHEN token.underlying_address = pool.quote_token_address
                            THEN pool.debt
                            ELSE 0
                            END) AS borrowed_amount
                    FROM {token_table} AS token
                    LEFT JOIN (
                        SELECT DISTINCT ON (ps.address)
                              ps.address
                            , ps.pledged_collateral
                            , ps.pool_size
                            , ps.t0debt * ps.pending_inflator as debt
                            , ps.collateral_token_address
                            , ps.quote_token_address
                            , ps.collateral_token_balance
                            , ps.quote_token_balance
                        FROM {pool_snapshot_table} ps
                        WHERE ps.datetime > (%s - INTERVAL '7 DAY')
                            AND ps.datetime <= %s
                        ORDER BY ps.address, ps.datetime DESC
                    ) AS pool
                        ON token.underlying_address = pool.collateral_token_address
                            OR token.underlying_address = pool.quote_token_address
                    GROUP BY 1
                ) AS sub
                LEFT JOIN (
                    SELECT DISTINCT ON (feed.underlying_address)
                          feed.price
                        , feed.underlying_address
                    FROM {price_feed_table} feed
                    WHERE feed.datetime > (%s - INTERVAL '7 DAY')
                        AND feed.datetime <= %s
                    ORDER BY feed.underlying_address, feed.datetime DESC
                ) pf
                    ON pf.underlying_address = sub.underlying_address
            )

            SELECT
                  sub.underlying_address
                , sub.symbol
                , sub.name
                , sub.underlying_price
                , sub.pool_count
                , sub.is_estimated_price
                , prev.pool_count AS prev_pool_count
                , prev.underlying_price AS prev_underlying_price
                , GREATEST(
                    (sub.collateral_amount + (sub.lended_amount - sub.borrowed_amount))
                    * sub.underlying_price
                  , 0) AS tvl
                , GREATEST(
                    (prev.collateral_amount * prev.underlying_price) +
                        (
                        (prev.lended_amount * prev.underlying_price) -
                        (prev.borrowed_amount * prev.underlying_price)
                    )
                  , 0) AS prev_tvl
            FROM(
                SELECT
                      token.underlying_address
                    , token.symbol
                    , token.name
                    , token.underlying_price
                    , token.is_estimated_price
                    , COUNT(pool.address) AS pool_count
                    , SUM(
                        CASE WHEN token.underlying_address = pool.collateral_token_address
                            THEN pool.collateral_token_balance
                            ELSE 0
                        END
                      ) AS collateral_amount
                    , SUM(
                        CASE WHEN token.underlying_address = pool.quote_token_address
                        THEN pool.pool_size
                        ELSE 0
                        END) AS lended_amount
                    , SUM(
                        CASE WHEN token.underlying_address = pool.quote_token_address
                        THEN pool.debt
                        ELSE 0
                        END) AS borrowed_amount
                FROM {token_table} AS token
                LEFT JOIN {pool_table} AS pool
                    ON token.underlying_address = pool.collateral_token_address
                        OR token.underlying_address = pool.quote_token_address
                GROUP BY 1, 2, 3, 4, 5
                ) AS sub
            LEFT JOIN previous AS prev
                ON sub.underlying_address = prev.underlying_address
        """.format(
            token_table=self.models.token._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            pool_snapshot_table=self.models.pool_snapshot._meta.db_table,
            price_feed_table=self.models.price_feed._meta.db_table,
        )

        sql_vars = [
            self.days_ago_dt,
            self.days_ago_dt,
            self.days_ago_dt,
            self.days_ago_dt,
        ]
        filters = []
        if search_filters:
            search_sql, search_vars = search_filters
            filters.append(search_sql)
            sql_vars.extend(search_vars)

        if filters:
            sql += " WHERE {}".format(" AND ".join(filters))

        return sql, sql_vars


class TokenView(BaseChainView):
    days_ago_required = False
    days_ago_default = 7
    days_ago_options = [1, 7, 30, 90, 365, 9999]

    def get(self, request, underlying_address):
        sql = """
            SELECT
                  underlying_address
                , symbol
                , name
                , decimals
                , is_erc721
                , underlying_price
                , is_estimated_price
            FROM {token_table}
            WHERE underlying_address = %s
        """.format(
            token_table=self.models.token._meta.db_table,
        )

        data = fetch_one(sql, [underlying_address])

        if not data:
            raise Http404

        return Response({"results": data}, status.HTTP_200_OK)


class TokenOverviewView(BaseChainView):
    days_ago_required = False
    days_ago_default = 7
    days_ago_options = [1, 7, 30, 90, 365, 9999]

    def get(self, request, underlying_address):
        sql_vars = {"days_ago_dt": self.days_ago_dt, "address": underlying_address}
        sql = """
            WITH previous AS (
                SELECT
                      sub.underlying_address
                    , sub.pool_count
                    , sub.collateral_amount
                    , sub.collateral_amount * pf.price AS collateral_amount_usd
                    , sub.lended_amount
                    , sub.lended_amount * pf.price AS lended_amount_usd
                    , sub.borrowed_amount
                    , sub.borrowed_amount * pf.price AS borrowed_amount_usd
                    , (sub.collateral_amount * pf.price) +
                        (
                        (sub.lended_amount * pf.price) -
                        (sub.borrowed_amount * pf.price)
                      ) AS tvl
                FROM (
                    SELECT
                          token.underlying_address
                        , COUNT(pool.address) AS pool_count
                        , SUM(
                            CASE WHEN token.underlying_address = pool.collateral_token_address
                            THEN pool.pledged_collateral
                            ELSE 0
                            END) AS collateral_amount
                        , SUM(
                            CASE WHEN token.underlying_address = pool.quote_token_address
                            THEN pool.pool_size
                            ELSE 0
                            END) AS lended_amount
                        , SUM(
                            CASE WHEN token.underlying_address = pool.quote_token_address
                            THEN pool.debt
                            ELSE 0
                            END) AS borrowed_amount
                    FROM {token_table} AS token
                    LEFT JOIN (
                        SELECT DISTINCT ON (ps.address)
                              ps.address
                            , ps.pledged_collateral
                            , ps.pool_size
                            , ps.debt
                            , ps.collateral_token_address
                            , ps.quote_token_address
                        FROM {pool_snapshot_table} ps
                        WHERE ps.datetime > (%(days_ago_dt)s - INTERVAL '7 DAY')
                            AND ps.datetime <= %(days_ago_dt)s
                        ORDER BY ps.address, ps.datetime DESC
                    ) AS pool
                        ON token.underlying_address = pool.collateral_token_address
                            OR token.underlying_address = pool.quote_token_address
                    WHERE token.underlying_address = %(address)s
                    GROUP BY 1
                ) AS sub
                LEFT JOIN (
                    SELECT DISTINCT ON (feed.underlying_address)
                          feed.price
                        , feed.underlying_address
                    FROM {price_feed_table} feed
                    WHERE feed.datetime > (%(days_ago_dt)s - INTERVAL '7 DAY')
                        AND feed.datetime <= %(days_ago_dt)s
                    ORDER BY feed.underlying_address, feed.datetime DESC
                ) pf
                    ON pf.underlying_address = sub.underlying_address
            )

            SELECT
                  sub.underlying_address
                , sub.symbol
                , sub.pool_count
                , sub.collateral_amount
                , sub.collateral_amount * sub.underlying_price AS collateral_amount_usd
                , sub.lended_amount
                , sub.lended_amount * sub.underlying_price AS lended_amount_usd
                , sub.borrowed_amount
                , sub.borrowed_amount * sub.underlying_price AS borrowed_amount_usd
                , GREATEST(
                    (sub.collateral_amount + (sub.lended_amount - sub.borrowed_amount))
                    * sub.underlying_price
                  , 0) AS tvl
                , prev.pool_count AS prev_pool_count
                , prev.collateral_amount AS prev_collateral_amount
                , prev.lended_amount AS prev_lended_amount
                , prev.borrowed_amount AS prev_borrowed_amount
                , prev.collateral_amount_usd  AS prev_collateral_amount_usd
                , prev.lended_amount_usd  AS prev_lended_amount_usd
                , prev.borrowed_amount_usd  AS prev_borrowed_amount_usd
                , GREATEST(
                    prev.tvl
                  , 0) AS prev_tvl
            FROM(
                SELECT
                      token.underlying_address
                    , token.symbol
                    , token.underlying_price
                    , COUNT(pool.address) AS pool_count
                    , SUM(
                        CASE WHEN token.underlying_address = pool.collateral_token_address
                        THEN pool.pledged_collateral
                        ELSE 0
                        END) AS collateral_amount
                    , SUM(
                        CASE WHEN token.underlying_address = pool.quote_token_address
                        THEN pool.pool_size
                        ELSE 0
                        END) AS lended_amount
                    , SUM(
                        CASE WHEN token.underlying_address = pool.quote_token_address
                        THEN pool.debt
                        ELSE 0
                        END) AS borrowed_amount
                FROM {token_table} AS token
                LEFT JOIN {pool_table} AS pool
                ON token.underlying_address = pool.collateral_token_address
                    OR token.underlying_address = pool.quote_token_address
                WHERE token.underlying_address = %(address)s
                GROUP BY 1, 2, 3
            ) AS sub
            LEFT JOIN previous AS prev
                ON sub.underlying_address = prev.underlying_address
        """.format(
            token_table=self.models.token._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            pool_snapshot_table=self.models.pool_snapshot._meta.db_table,
            price_feed_table=self.models.price_feed._meta.db_table,
        )

        data = fetch_one(sql, sql_vars)

        if not data:
            raise Http404

        return Response({"results": data}, status.HTTP_200_OK)


class TokenPoolsView(RawSQLPaginatedChainView):
    days_ago_required = False
    days_ago_default = 7
    days_ago_options = [1, 7, 30, 90, 365, 9999]
    default_order = "-tvl"
    ordering_fields = [
        "pledged_collateral",
        "pool_size",
        "debt",
        "borrow_rate",
        "lend_rate",
        "total_ajna_burned",
        "tvl",
    ]

    def get_raw_sql(self, search_filters, **kwargs):
        underlying_address = kwargs["underlying_address"]
        sql_vars = [
            self.days_ago_dt,
            self.days_ago_dt,
            underlying_address,
            underlying_address,
        ]

        sql = """
            {}
            WHERE pool.collateral_token_address = %s
            OR pool.quote_token_address = %s
        """.format(
            POOLS_SQL.format(
                token_table=self.models.token._meta.db_table,
                pool_table=self.models.pool._meta.db_table,
                pool_snapshot_table=self.models.pool_snapshot._meta.db_table,
            )
        )
        return sql, sql_vars


class TokenArbitragePoolsView(RawSQLPaginatedChainView):
    days_ago_required = False
    days_ago_default = 7
    days_ago_options = [1, 7, 30, 90, 365, 9999]
    default_order = "-collateral_token_underlying_price"
    ordering_fields = [
        "lup",
        "htp",
        "hpb",
        "collateral_token_underlying_price",
        "collateral_token_symbol",
        "quote_token_symbol",
    ]

    def get_raw_sql(self, search_filters, **kwargs):
        underlying_address = kwargs["underlying_address"]

        sql = """
            WITH previous AS (
                SELECT DISTINCT ON (ps.address)
                      ps.address
                    , ps.lup
                    , ps.htp
                    , ps.hpb
                    , pfc.price AS collateral_token_underlying_price
                FROM {pool_snapshot_table} ps
                JOIN {pool_table} pool
                    ON ps.address = pool.address
                LEFT JOIN (
                    SELECT DISTINCT ON (feed.underlying_address)
                          feed.price
                        , feed.underlying_address
                    FROM {price_feed_table} feed
                    WHERE feed.datetime > (%(days_ago_dt)s - INTERVAL '7 DAY')
                        AND feed.datetime <= %(days_ago_dt)s
                    ORDER BY feed.underlying_address, feed.datetime DESC
                ) pfc
                    ON pfc.underlying_address = pool.collateral_token_address
                WHERE ps.datetime > (%(days_ago_dt)s - INTERVAL '7 DAY')
                    AND ps.datetime <= %(days_ago_dt)s
                ORDER BY ps.address, ps.datetime DESC
            )

            SELECT
                  pool.address
                , pool.lup
                , pool.htp
                , pool.hpb
                , collateral_token.symbol AS collateral_token_symbol
                , collateral_token.underlying_price AS collateral_token_underlying_price
                , collateral_token.underlying_address AS collateral_token_address
                , quote_token.symbol AS quote_token_symbol
                , quote_token.underlying_address AS quote_token_address
                , prev.lup AS prev_lup
                , prev.htp AS prev_htp
                , prev.hpb AS prev_hpb
                , prev.collateral_token_underlying_price AS prev_collateral_token_underlying_price
            FROM {pool_table} AS pool
            JOIN {token_table} AS collateral_token
                ON pool.collateral_token_address = collateral_token.underlying_address
            JOIN {token_table} AS quote_token
                ON pool.quote_token_address = quote_token.underlying_address
            LEFT JOIN previous AS prev
                ON pool.address = prev.address
            WHERE (pool.collateral_token_address = %(address)s
                OR pool.quote_token_address = %(address)s)
                AND pool.hpb * quote_token.underlying_price >= collateral_token.underlying_price
        """.format(
            token_table=self.models.token._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            pool_snapshot_table=self.models.pool_snapshot._meta.db_table,
            price_feed_table=self.models.price_feed._meta.db_table,
        )
        sql_vars = {"days_ago_dt": self.days_ago_dt, "address": underlying_address}

        return sql, sql_vars
