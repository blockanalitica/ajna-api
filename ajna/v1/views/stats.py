from django.http import Http404
from rest_framework import status
from rest_framework.response import Response

from ajna.utils.db import fetch_one
from ajna.utils.views import BaseChainView


class OverviewView(BaseChainView):
    days_ago_required = False
    days_ago_default = 7
    days_ago_options = [1, 7, 30, 365]

    def get(self, request):
        sql_vars = [self.days_ago_dt]
        sql = """
            WITH previous AS (
                SELECT DISTINCT ON (ps.address)
                      ps.address
                    , ps.total_ajna_burned
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
                  SUM(sub.tvl) AS total_tvl
                , SUM(sub.pledged_collateral * sub.collateral_token_underlying_price)
                  AS total_pledged_collateral
                , SUM(sub.pool_size * sub.quote_token_underlying_price) AS total_pool_size
                , SUM(sub.debt * sub.quote_token_underlying_price) AS total_current_debt
                , SUM(sub.total_ajna_burned) AS total_ajna_burned
                , SUM(sub.prev_tvl) AS prev_total_tvl
                , SUM(sub.prev_pledged_collateral_usd) AS prev_total_pledged_collateral
                , SUM(sub.prev_pool_size_usd) AS prev_total_pool_size
                , SUM(sub.prev_debt_usd) AS prev_total_current_debt
                , SUM(sub.prev_total_ajna_burned) AS prev_total_ajna_burned
            FROM (
                SELECT
                      pool.pledged_collateral
                    , pool.pool_size
                    , pool.debt
                    , pool.total_ajna_burned
                    , collateral_token.underlying_price AS collateral_token_underlying_price
                    , quote_token.underlying_price AS quote_token_underlying_price
                    , (pool.collateral_token_balance * collateral_token.underlying_price) +
                      (pool.quote_token_balance * quote_token.underlying_price) AS tvl
                    , prev.pledged_collateral_usd AS prev_pledged_collateral_usd
                    , prev.pool_size_usd AS prev_pool_size_usd
                    , prev.debt_usd AS prev_debt_usd
                    , prev.total_ajna_burned AS prev_total_ajna_burned
                    , prev.tvl AS prev_tvl
                FROM {pool_table} AS pool
                JOIN {token_table} AS collateral_token
                    ON pool.collateral_token_address = collateral_token.underlying_address
                JOIN {token_table} AS quote_token
                    ON pool.quote_token_address = quote_token.underlying_address
                FULL JOIN previous AS prev
                    ON prev.address = pool.address
            ) AS sub
        """.format(
            token_table=self.models.token._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            pool_snapshot_table=self.models.pool_snapshot._meta.db_table,
        )

        data = fetch_one(sql, sql_vars)

        if not data:
            raise Http404

        return Response({"results": data}, status.HTTP_200_OK)
