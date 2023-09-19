from ajna.utils.views import RawSQLPaginatedChainView

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


class PoolsView(RawSQLPaginatedChainView):
    """
    A view for retrieving a paginated list of pools and their related
    collateral and quote token information.

    This view uses raw SQL to efficiently fetch the data from the database and inherits from
    BaseChainView and RawSQLPaginatedApiView to handle pagination and filtering. It also allows
    specifying a range of days for which to fetch the data.

    Attributes:
        days_ago_required (bool): Flag indicating if the `days_ago` parameter is required.
        days_ago_default (int): Default value for the `days_ago` parameter.
        days_ago_options (list): List of allowed values for the `days_ago` parameter.
    """

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

    # def get_count_sql(self, **kwargs):
    #     sql = """
    #         SELECT COUNT(*) FROM {pool_table}
    #     """.format(
    #         pool_table=self.models.pool._meta.db_table
    #     )
    #     return sql, []
