from django.http import Http404
from rest_framework import status
from rest_framework.response import Response

from ajna.utils.db import fetch_all, fetch_one
from ajna.utils.utils import date_to_timestamp
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

    def get_raw_sql(self, **kwargs):
        sql = """
            SELECT
                  la.uid
                , la.settle_time
                , la.neutral_price
                , la.kick_time
                , la.debt
                , la.collateral
                , la.borrower
                , la.wallet_address
                , la.debt * la.debt_underlying_price AS debt_usd
                , la.collateral * la.collateral_underlying_price AS collateral_usd
                , la.pool_address
                , tc.symbol AS collateral_token_symbol
                , td.symbol AS debt_token_symbol
            FROM {liqudation_auction_table} la
            LEFT JOIN {token_table} tc
                ON la.collateral_token_address = tc.underlying_address
            LEFT JOIN {token_table} td
                ON la.debt_token_address = td.underlying_address
            WHERE la.settled = TRUE
                AND la.settle_time >= %s
        """.format(
            token_table=self.models.token._meta.db_table,
            liqudation_auction_table=self.models.liqudation_auction._meta.db_table,
        )
        sql_vars = [self.days_ago_dt.timestamp()]
        return sql, sql_vars


class AuctionsSettledGraphsView(BaseChainView):
    def _get_collateral_graph_data(self, from_ts, date_trunc):
        sql = """
            SELECT
                DATE_TRUNC(%s, TO_TIMESTAMP(la.settle_time)) AS date
                , tc.symbol AS symbol
                , SUM(la.collateral) AS amount
                , SUM(la.collateral * la.collateral_underlying_price) AS amount_usd
            FROM {liqudation_auction_table} la
            LEFT JOIN {token_table} tc
                ON la.collateral_token_address = tc.underlying_address
            WHERE la.settled = TRUE
                AND la.settle_time >= %s
            GROUP BY 1, 2
        """.format(
            token_table=self.models.token._meta.db_table,
            liqudation_auction_table=self.models.liqudation_auction._meta.db_table,
        )

        auctions = fetch_all(sql, [date_trunc, from_ts])
        return auctions

    def _get_debt_graph_data(self, from_ts, date_trunc):
        sql = """
            SELECT
                DATE_TRUNC(%s, TO_TIMESTAMP(la.settle_time)) AS date
                , td.symbol AS symbol
                , SUM(la.debt) AS amount
                , SUM(la.debt * la.debt_underlying_price) AS amount_usd
            FROM {liqudation_auction_table} la
            LEFT JOIN {token_table} td
                ON la.debt_token_address = td.underlying_address
            WHERE la.settled = TRUE
                AND la.settle_time >= %s
            GROUP BY 1, 2
        """.format(
            token_table=self.models.token._meta.db_table,
            liqudation_auction_table=self.models.liqudation_auction._meta.db_table,
        )

        auctions = fetch_all(sql, [date_trunc, from_ts])
        return auctions

    def get(self, request, graph_type):
        date_trunc = "day" if self.days_ago <= 30 else "month"

        # Always select the full day, otherwise bar chart doesn't make sense
        from_ts = date_to_timestamp(self.days_ago_dt)

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
        sql_change = """
            SELECT
                  SUM(la.debt * la.debt_underlying_price) AS debt_usd
                , SUM(la.collateral * la.collateral_underlying_price) AS collateral_usd
                , COUNT(la.uid) AS count
            FROM {liqudation_auction_table} la
            WHERE la.settled = TRUE
                AND la.settle_time >= %s
        """.format(
            liqudation_auction_table=self.models.liqudation_auction._meta.db_table,
        )

        change_data = fetch_one(sql_change, [self.days_ago_dt.timestamp()])

        sql = """
            SELECT
                  SUM(la.debt * la.debt_underlying_price) AS debt_usd
                , SUM(la.collateral * la.collateral_underlying_price) AS collateral_usd
                , COUNT(la.uid) AS count
            FROM {liqudation_auction_table} la
            WHERE la.settled = TRUE
        """.format(
            liqudation_auction_table=self.models.liqudation_auction._meta.db_table,
        )

        data = fetch_one(sql, [])

        change_sql = "{} AND la.settle_time >= %s".format(sql)

        change_data = fetch_one(change_sql, [self.days_ago_dt.timestamp()])

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
                  la.uid
                , la.pool_address
                , la.kick_time
                , la.debt
                , la.debt_remaining
                , la.collateral
                , la.collateral_remaining
                , la.borrower
                , la.wallet_address
                , tc.symbol AS collateral_token_symbol
                , td.symbol AS debt_token_symbol
            FROM {liqudation_auction_table} la
            LEFT JOIN {token_table} tc
                ON la.collateral_token_address = tc.underlying_address
            LEFT JOIN {token_table} td
                ON la.debt_token_address = td.underlying_address
            WHERE la.settled = False
        """.format(
            token_table=self.models.token._meta.db_table,
            liqudation_auction_table=self.models.liqudation_auction._meta.db_table,
        )

        sql_vars = []
        return sql, sql_vars
