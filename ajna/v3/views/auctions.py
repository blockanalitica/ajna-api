import json

from django.http import Http404
from rest_framework import status
from rest_framework.response import Response

from ajna.constants import MAX_INFLATED_PRICE
from ajna.utils.db import fetch_all, fetch_one
from ajna.utils.views import BaseChainView, RawSQLPaginatedChainView

from ..modules.at_risk import WALLETS_AT_RISK_SQL


class AuctionsSettledView(RawSQLPaginatedChainView):
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
                , w.eoa AS borrower_eoa
                , at.debt * ak.quote_token_price AS debt_usd
                , at.collateral * ak.collateral_token_price AS collateral_usd
                , at.pool_address
                , ct.symbol AS collateral_token_symbol
                , qt.symbol AS quote_token_symbol
            FROM {auction_table} at
            JOIN {auction_kick_table} ak
                ON at.uid = ak.auction_uid
            JOIN {pool_table} p
                ON at.pool_address = p.address
            LEFT JOIN {wallet_table} w
                on at.borrower = w.address
            JOIN {token_table} AS ct
                ON p.collateral_token_address = ct.underlying_address
            JOIN {token_table} AS qt
                ON p.quote_token_address = qt.underlying_address
            WHERE at.settled = TRUE
                AND at.settle_time >= %s
        """.format(
            token_table=self.models.token._meta.db_table,
            auction_table=self.models.auction._meta.db_table,
            auction_kick_table=self.models.auction_kick._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            wallet_table=self.models.wallet._meta.db_table,
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
                , SUM(at.collateral * ak.collateral_token_price) AS amount_usd
            FROM {auction_table} at
            JOIN {auction_kick_table} ak
                ON at.uid = ak.auction_uid
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
            auction_kick_table=self.models.auction_kick._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
        )

        auctions = fetch_all(sql, [date_trunc, from_ts])
        return auctions

    def _get_debt_graph_data(self, from_ts, date_trunc):
        sql = """
            SELECT
                  DATE_TRUNC(%s, at.settle_time) AS date
                , qt.symbol AS symbol
                , SUM(at.debt) AS amount
                , SUM(at.debt * ak.quote_token_price) AS amount_usd
            FROM {auction_table} at
            JOIN {auction_kick_table} ak
                ON at.uid = ak.auction_uid
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
            auction_kick_table=self.models.auction_kick._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
        )

        auctions = fetch_all(sql, [date_trunc, from_ts])
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
                  SUM(at.debt * ak.quote_token_price) AS debt_usd
                , SUM(at.collateral * ak.collateral_token_price) AS collateral_usd
                , COUNT(at.uid) AS count
            FROM {auction_table} at
            JOIN {auction_kick_table} ak
                ON at.uid = ak.auction_uid
            WHERE at.settled = TRUE
        """.format(
            auction_table=self.models.auction._meta.db_table,
            auction_kick_table=self.models.auction_kick._meta.db_table,
        )

        data = fetch_one(sql, [])
        change_sql = "{} AND at.settle_time >= %s".format(sql)
        change_data = fetch_one(change_sql, [self.days_ago_dt])

        data["change"] = change_data
        return Response(data, status.HTTP_200_OK)


class AuctionsActiveView(RawSQLPaginatedChainView):
    default_order = "-collateral"
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
                , at.debt_remaining
                , at.debt_remaining * ak.quote_token_price AS debt_remaining_usd
                , at.collateral_remaining
                , at.collateral_remaining * ak.collateral_token_price AS collateral_remaining_usd
                , at.borrower
                , w.eoa AS borrower_eoa
                , ct.symbol AS collateral_token_symbol
                , qt.symbol AS quote_token_symbol
                , ak.block_datetime AS kick_time
                , p.lup
                , p.lup * ak.quote_token_price AS lup_usd
            FROM {auction_table} at
            JOIN {auction_kick_table} ak
                ON at.uid = ak.auction_uid
            JOIN {pool_table} p
                ON at.pool_address = p.address
            LEFT JOIN {wallet_table} w
                on at.borrower = w.address
            JOIN {token_table} AS ct
                ON p.collateral_token_address = ct.underlying_address
            JOIN {token_table} AS qt
                ON p.quote_token_address = qt.underlying_address
            WHERE at.settled = False
        """.format(
            token_table=self.models.token._meta.db_table,
            auction_table=self.models.auction._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            auction_kick_table=self.models.auction_kick._meta.db_table,
            wallet_table=self.models.wallet._meta.db_table,
        )

        sql_vars = []
        return sql, sql_vars


class AuctionView(BaseChainView):
    def get(self, request, uid):
        sql_vars = [uid]
        sql = """
            SELECT
                  at.uid
                , at.pool_address
                , at.borrower
                , w.eoa AS borrower_eoa
                , at.kicker
                , at.collateral
                , at.collateral * ak.collateral_token_price AS collateral_usd
                , at.collateral_remaining
                , at.collateral_remaining * ak.collateral_token_price AS collateral_remaining_usd
                , at.debt
                , at.debt * ak.quote_token_price AS debt_usd
                , at.debt_remaining
                , at.debt_remaining * ak.quote_token_price AS debt_remaining_usd
                , at.settled
                , at.settle_time
                , at.bond_factor
                , at.bond_size
                , at.neutral_price
                , at.last_take_price
                , ak.bond
                , ak.bond * ak.quote_token_price AS bond_usd
                , ak.locked
                , ak.reference_price
                , ak.starting_price
                , ct.symbol AS collateral_token_symbol
                , qt.symbol AS quote_token_symbol
                , p.lup
            FROM {auction_table} at
            LEFT JOIN {wallet_table} w
                on at.borrower = w.address
            JOIN {auction_kick_table} ak
                ON at.uid = ak.auction_uid
            JOIN {pool_table} p
                ON at.pool_address = p.address
            JOIN {token_table} AS ct
                ON p.collateral_token_address = ct.underlying_address
            JOIN {token_table} AS qt
                ON p.quote_token_address = qt.underlying_address
            WHERE at.uid = %s
        """.format(
            auction_table=self.models.auction._meta.db_table,
            auction_kick_table=self.models.auction_kick._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
            wallet_table=self.models.wallet._meta.db_table,
        )

        data = fetch_one(sql, sql_vars)

        if not data:
            raise Http404

        return Response(data, status.HTTP_200_OK)


class AuctionEventsView(RawSQLPaginatedChainView):
    default_order = "-order_index"

    def get_raw_sql(self, auction_uid, **kwargs):
        sql = """
            SELECT
                  at.order_index
                , 'Take' AS event
                , at.auction_uid
                , at.pool_address
                , at.block_number
                , at.block_datetime
                , at.transaction_hash
                , jsonb_build_object(
                    'taker', at.taker,
                    'amount', at.amount::text,
                    'collateral', at.collateral::text,
                    'auction_price', at.auction_price::text,
                    'bond_change', at.bond_change::text,
                    'is_reward', at.is_reward
                ) AS data
            FROM {auction_take_table} at
            WHERE at.auction_uid = %s

            UNION

            SELECT
                  abt.order_index
                , 'Bucket Take' AS event
                , abt.auction_uid
                , abt.pool_address
                , abt.block_number
                , abt.block_datetime
                , abt.transaction_hash
                , jsonb_build_object(
                    'taker', abt.taker,
                    'index', abt.index,
                    'amount', abt.amount::text,
                    'collateral', abt.collateral::text,
                    'auction_price', abt.auction_price::text,
                    'bond_change', abt.bond_change::text,
                    'is_reward', abt.is_reward
                ) AS data
            FROM {auction_bucket_take_table} abt
            WHERE abt.auction_uid = %s

            UNION

            SELECT
                  akt.order_index
                , 'Kick' AS event
                , akt.auction_uid
                , akt.pool_address
                , akt.block_number
                , akt.block_datetime
                , akt.transaction_hash
                , jsonb_build_object(
                    'kicker', akt.kicker,
                    'debt', akt.debt::text,
                    'collateral', akt.collateral::text,
                    'bond', akt.bond::text
                ) AS data
            FROM {auction_kick_table} akt
            WHERE akt.auction_uid = %s

            UNION

            SELECT
                  ast.order_index
                , 'Settle' AS event
                , ast.auction_uid
                , ast.pool_address
                , ast.block_number
                , ast.block_datetime
                , ast.transaction_hash
                , jsonb_build_object(
                    'settled_debt', ast.settled_debt::text
                ) AS data
            FROM {auction_settle_table} ast
            WHERE ast.auction_uid = %s

            UNION

            SELECT
                  aast.order_index
                , 'Auction Settle' AS event
                , aast.auction_uid
                , aast.pool_address
                , aast.block_number
                , aast.block_datetime
                , aast.transaction_hash
                , jsonb_build_object(
                    'collateral', aast.collateral::text
                ) AS data
            FROM {auction_auction_settle_table} aast
            WHERE aast.auction_uid = %s

            UNION

            SELECT
                  aanst.order_index
                , 'Auction NFT Settle' AS event
                , aanst.auction_uid
                , aanst.pool_address
                , aanst.block_number
                , aanst.block_datetime
                , aanst.transaction_hash
                , jsonb_build_object(
                    'collateral', aanst.collateral::text,
                    'index', aanst.index::text
                ) AS data
            FROM {auction_auction_nft_settle_table} aanst
            WHERE aanst.auction_uid = %s
        """.format(
            auction_take_table=self.models.auction_take._meta.db_table,
            auction_bucket_take_table=self.models.auction_bucket_take._meta.db_table,
            auction_kick_table=self.models.auction_kick._meta.db_table,
            auction_settle_table=self.models.auction_settle._meta.db_table,
            auction_auction_settle_table=self.models.auction_auction_settle._meta.db_table,
            auction_auction_nft_settle_table=self.models.auction_auction_nft_settle._meta.db_table,
        )

        sql_vars = [auction_uid] * 6
        return sql, sql_vars

    def serialize_data(self, data):
        for row in data:
            row["data"] = json.loads(row["data"])
        return data


class AuctionsToKickView(RawSQLPaginatedChainView):
    default_order = "-debt"

    def get_raw_sql(self, **kwargs):
        sql = WALLETS_AT_RISK_SQL.format(
            current_wallet_position_table=self.models.current_wallet_position._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
            wallet_table=self.models.wallet._meta.db_table,
        )
        sql_vars = [MAX_INFLATED_PRICE, 0]
        return sql, sql_vars
