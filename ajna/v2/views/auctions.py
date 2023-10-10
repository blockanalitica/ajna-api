from django.db import connection
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response

from ajna.utils.db import fetch_all, fetch_one
from ajna.utils.views import BaseChainView, RawSQLPaginatedChainView


class AuctionsSettledView(RawSQLPaginatedChainView):
    """
    A view that returns a paginated list of settled auctions.

    """

    default_order = "-settle_time"
    ordering_fields = [
        "collateral",
        "debt",
        "settle_time",
    ]
    days_ago_required = True

    def get_raw_sql(self, **kwargs):
        sql = """
            SELECT
                  at.uid
                , at.settle_time
                , at.neutral_price
                , at.debt
                , at.collateral
                , at.borrower
                , at.debt * qt.underlying_price AS debt_usd
                , at.collateral * ct.underlying_price AS collateral_usd
                , at.pool_address
                , ct.symbol AS collateral_token_symbol
                , qt.symbol AS debt_token_symbol
            FROM {auction_table} at
            JOIN {pool_table} p
                ON at.pool_address = p.address
            JOIN {token_table} AS ct
                ON p.collateral_token_address = ct.underlying_address
           JOIN {token_table} AS qt
                ON p.quote_token_address = qt.underlying_address
            WHERE at.settled = TRUE
                AND at.settle_time >= %s
        """.format(
            token_table=self.models.token._meta.db_table,
            auction_table=self.models.auction._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
        )
        sql_vars = [self.days_ago_dt]
        return sql, sql_vars


class AuctionsSettledGraphsView(BaseChainView):
    def _get_collateral_graph_data(self, from_ts, date_trunc):
        sql = """
            SELECT
                DATE_TRUNC(%s, at.settle_time) AS date
                , ct.symbol AS symbol
                , SUM(at.collateral) AS amount
                , SUM(at.collateral * ct.underlying_price) AS amount_usd
            FROM {auction_table} at
            JOIN {pool_table} p
                ON at.pool_address = p.address
            JOIN {token_table} AS ct
                ON p.collateral_token_address = ct.underlying_address
            WHERE at.settled = TRUE
                AND at.settle_time >= %s
            GROUP BY 1, 2
        """.format(
            token_table=self.models.token._meta.db_table,
            auction_table=self.models.auction._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
        )

        with connection.cursor() as cursor:
            cursor.execute(sql, [date_trunc, from_ts])
            auctions = fetch_all(cursor)
        return auctions

    def _get_debt_graph_data(self, from_ts, date_trunc):
        sql = """
            SELECT
                DATE_TRUNC(%s, at.settle_time) AS date
                , qt.symbol AS symbol
                , SUM(at.debt) AS amount
                , SUM(at.debt * qt.underlying_price) AS amount_usd
            FROM {auction_table} at
            JOIN {pool_table} p
                ON at.pool_address = p.address
            JOIN {token_table} AS qt
                ON p.quote_token_address = qt.underlying_address
            WHERE at.settled = TRUE
                AND at.settle_time >= %s
            GROUP BY 1, 2
        """.format(
            token_table=self.models.token._meta.db_table,
            auction_table=self.models.auction._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
        )

        with connection.cursor() as cursor:
            cursor.execute(sql, [date_trunc, from_ts])
            auctions = fetch_all(cursor)
        return auctions

    def get(self, request, graph_type):
        date_trunc = "day" if self.days_ago <= 30 else "month"

        # Always select the full day, otherwise bar chart doesn't make sense
        from_ts = self.days_ago_dt.date()

        match graph_type:
            case "collateral":
                data = self._get_collateral_graph_data(from_ts, date_trunc)
            case "debt":
                data = self._get_debt_graph_data(from_ts, date_trunc)
            case _:
                raise Http404

        return Response(data, status.HTTP_200_OK)


class AuctionsSettledOverviewView(BaseChainView):
    def get(self, request):
        sql = """
             SELECT
                  SUM(at.debt * qt.underlying_price) AS debt_usd
                , SUM(at.collateral * ct.underlying_price) AS collateral_usd
                , COUNT(at.uid) AS count
            FROM {auction_table} at
            JOIN {pool_table} p
                ON at.pool_address = p.address
            JOIN {token_table} AS ct
                ON p.collateral_token_address = ct.underlying_address
            JOIN {token_table} AS qt
                ON p.quote_token_address = qt.underlying_address
            WHERE at.settled = TRUE
        """.format(
            auction_table=self.models.auction._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
        )
        with connection.cursor() as cursor:
            cursor.execute(sql, [])
            data = fetch_one(cursor)

        change_sql = "{} AND at.settle_time >= %s".format(sql)
        with connection.cursor() as cursor:
            cursor.execute(change_sql, [self.days_ago_dt])
            change_data = fetch_one(cursor)

        data["change"] = change_data
        return Response(data, status.HTTP_200_OK)


class AuctionsActiveView(RawSQLPaginatedChainView):
    """
    A view that returns a paginated list of settled auctions.

    """

    default_order = "-kick_time"
    ordering_fields = [
        "collateral",
        "debt",
        "kick_time",
    ]

    def get_raw_sql(self, **kwargs):
        sql = """
            SELECT
                  at.uid
                , at.pool_address
                , at.debt
                , at.debt_remaining
                , at.collateral
                , at.collateral_remaining
                , at.borrower
                , ct.symbol AS collateral_token_symbol
                , qt.symbol AS debt_token_symbol
            FROM {auction_table} at
            JOIN {pool_table} p
                ON at.pool_address = p.address
            JOIN {token_table} AS ct
                ON p.collateral_token_address = ct.underlying_address
            JOIN {token_table} AS qt
                ON p.quote_token_address = qt.underlying_address
            WHERE at.settled = False
        """.format(
            token_table=self.models.token._meta.db_table,
            auction_table=self.models.liqudation_auction._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
        )

        sql_vars = []
        return sql, sql_vars
