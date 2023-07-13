from . import RawSQLPaginatedChainView


class TokensView(RawSQLPaginatedChainView):
    """
    A view that returns a paginated list of tokens along with the count of
    associated pools (as collateral or quote tokens).

    Attributes:
        days_ago_required (bool): Flag indicating if the `days_ago` parameter is required.
        days_ago_default (int): Default value for the `days_ago` parameter.
        days_ago_options (list): List of allowed values for the `days_ago` parameter.
    """

    days_ago_required = False
    days_ago_default = 7
    days_ago_options = [1, 7, 30, 365]
    default_order = "-tvl"
    ordering_fields = [
        "symbol",
        "name",
        "pool_count",
        "collateral_amount",
        "quote_amount",
        "tvl",
    ]
    search_fields = ["sub.symbol", "sub.name"]

    def get_raw_sql(self, search_filters, **kwargs):
        sql = """
            WITH previous AS (
                SELECT
                      sub.underlying_address
                    , sub.pool_count
                    , sub.collateral_amount
                    , sub.quote_amount
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
                                THEN pool.quote_token_balance
                                ELSE 0
                            END
                          ) AS quote_amount
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
                        WHERE ps.datetime <= %s
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
                    WHERE feed.datetime <= %s
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
                , prev.pool_count AS prev_pool_count
                , prev.underlying_price AS prev_underlying_price
                , COALESCE(
                    ((sub.collateral_amount + sub.quote_amount) * sub.underlying_price), 0
                  ) AS tvl
                , COALESCE(
                    ((prev.collateral_amount + prev.quote_amount) * prev.underlying_price), 0
                  ) AS prev_tvl
            FROM(
                SELECT
                      token.underlying_address
                    , token.symbol
                    , token.name
                    , token.underlying_price
                    , COUNT(pool.address) AS pool_count
                    , SUM(
                        CASE WHEN token.underlying_address = pool.collateral_token_address
                            THEN pool.pledged_collateral
                            ELSE 0
                        END
                      ) AS collateral_amount
                    , SUM(
                        CASE WHEN token.underlying_address = pool.quote_token_address
                            THEN pool.pool_size - pool.debt
                            ELSE 0
                        END
                      ) AS quote_amount
                FROM {token_table} AS token
                LEFT JOIN {pool_table} AS pool
                    ON token.underlying_address = pool.collateral_token_address
                        OR token.underlying_address = pool.quote_token_address
                GROUP BY 1, 2, 3, 4
                ) AS sub
            LEFT JOIN previous AS prev
                ON sub.underlying_address = prev.underlying_address
        """.format(
            token_table=self.models.token._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            pool_snapshot_table=self.models.pool_snapshot._meta.db_table,
            price_feed_table=self.models.price_feed._meta.db_table,
        )

        sql_vars = [self.days_ago_dt, self.days_ago_dt]
        filters = []
        if search_filters:
            search_sql, search_vars = search_filters
            filters.append(search_sql)
            sql_vars.extend(search_vars)

        if filters:
            sql += " WHERE {}".format(" AND ".join(filters))

        return sql, sql_vars
