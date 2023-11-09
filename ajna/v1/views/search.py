from rest_framework import status
from rest_framework.response import Response

from ajna.utils.db import fetch_all
from ajna.utils.views import BaseChainView


class SearchView(BaseChainView):
    def _get_pools(self, search_term):
        sql = """
            SELECT
                *
            FROM (
                SELECT
                    pool.address,
                    collateral_token.symbol AS collateral_token_symbol,
                    collateral_token.name AS collateral_token_name,
                    quote_token.symbol AS quote_token_symbol,
                    quote_token.name AS quote_token_name,
                    (pool.collateral_token_balance * collateral_token.underlying_price) +
                    (pool.quote_token_balance * quote_token.underlying_price) AS tvl
                FROM
                    {pool_table} AS pool
                JOIN
                    {token_table} AS collateral_token
                ON
                    pool.collateral_token_address = collateral_token.underlying_address
                JOIN
                    {token_table} AS quote_token
                ON
                    pool.quote_token_address = quote_token.underlying_address
                WHERE collateral_token.symbol ILIKE %s
                    OR collateral_token.name ILIKE %s
                    OR quote_token.symbol ILIKE %s
                    OR quote_token.name ILIKE %s
            ) AS x
            ORDER BY tvl DESC NULLS LAST
            LIMIT 3
        """.format(
            token_table=self.models.token._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
        )

        pools = fetch_all(sql, [search_term] * 4)
        return pools

    def _get_tokens(self, search_term):
        sql = """
            SELECT
                *
            FROM (
                SELECT
                    sub.underlying_address,
                    sub.symbol,
                    sub.name,
                    (sub.collateral_amount + sub.quote_amount) * sub.underlying_price AS tvl
                FROM
                    (SELECT
                        token.underlying_address,
                        token.symbol,
                        token.name,
                        token.underlying_price,
                        SUM(
                            CASE WHEN token.underlying_address = pool.collateral_token_address
                            THEN pool.pledged_collateral
                            ELSE 0
                            END) AS collateral_amount,
                        SUM(
                            CASE WHEN token.underlying_address = pool.quote_token_address
                            THEN pool.pool_size - pool.debt
                            ELSE 0
                            END) AS quote_amount
                    FROM
                        {token_table} AS token
                    LEFT JOIN
                        {pool_table} AS pool
                    ON
                        token.underlying_address = pool.collateral_token_address
                        OR token.underlying_address = pool.quote_token_address
                    WHERE token.symbol ILIKE %s
                        OR token.name ILIKE %s
                    GROUP BY
                        token.underlying_address,
                        token.symbol,
                        token.name,
                        token.underlying_price) AS sub
            ) AS x
            ORDER BY tvl DESC NULLS LAST
            LIMIT 3
        """.format(
            token_table=self.models.token._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
        )

        tokens = fetch_all(sql, [search_term] * 2)
        return tokens

    def get(self, request):
        search_term = request.GET.get("search", "")
        search_term = "%{}%".format(search_term)

        pools = self._get_pools(search_term)
        tokens = self._get_tokens(search_term)

        return Response({"pools": pools, "tokens": tokens}, status.HTTP_200_OK)
