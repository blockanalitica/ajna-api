import json

from django.db import connection
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response

from ajna.utils.db import fetch_one
from ajna.utils.views import BaseChainView, RawSQLPaginatedChainView


class ReserveAuctionsActiveView(RawSQLPaginatedChainView):
    default_order = "-block_number"

    def get_raw_sql(self, **kwargs):
        sql = """
            SELECT
                  ra.uid
                , ra.pool_address
                , ra.claimable_reserves
                , ra.claimable_reserves_remaining
                , ra.last_take_price
                , ra.burn_epoch
                , ra.ajna_burned
                , rak.block_number
                , rak.block_datetime AS kick_datetime
                , ct.symbol AS collateral_token_symbol
                , qt.symbol AS quote_token_symbol
                , 'active' AS type
                , COUNT(rat.order_index) as take_count
            FROM {reserve_auction_table} ra
            JOIN {reserve_auction_kick_table} rak
                ON rak.reserve_auction_uid = ra.uid
            LEFT JOIN {reserve_auction_take_table} rat
                ON rat.reserve_auction_uid = ra.uid
            JOIN {pool_table} p
                ON ra.pool_address = p.address
            JOIN {token_table} AS ct
                ON p.collateral_token_address = ct.underlying_address
            JOIN {token_table} AS qt
                ON p.quote_token_address = qt.underlying_address
            WHERE rak.block_datetime + INTERVAL '72 hours' > CURRENT_TIMESTAMP
            GROUP BY 1,2,3,4,5,6,7,8,9,10,11,12
        """.format(
            reserve_auction_table=self.models.reserve_auction._meta.db_table,
            reserve_auction_kick_table=self.models.reserve_auction_kick._meta.db_table,
            reserve_auction_take_table=self.models.reserve_auction_take._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
        )
        sql_vars = []
        return sql, sql_vars


class ReserveAuctionsExpiredView(RawSQLPaginatedChainView):
    default_order = "-block_number"

    def get_raw_sql(self, **kwargs):
        sql = """
            SELECT
                  ra.uid
                , ra.pool_address
                , ra.claimable_reserves
                , ra.claimable_reserves_remaining
                , ra.last_take_price
                , ra.burn_epoch
                , ra.ajna_burned
                , rak.block_number
                , ct.symbol AS collateral_token_symbol
                , qt.symbol AS quote_token_symbol
                , 'expired' AS type
                , COUNT(rat.order_index) as take_count
            FROM {reserve_auction_table} ra
            JOIN {reserve_auction_kick_table} rak
                ON rak.reserve_auction_uid = ra.uid
            LEFT JOIN {reserve_auction_take_table} rat
                ON rat.reserve_auction_uid = ra.uid
            JOIN {pool_table} p
                ON ra.pool_address = p.address
            JOIN {token_table} AS ct
                ON p.collateral_token_address = ct.underlying_address
            JOIN {token_table} AS qt
                ON p.quote_token_address = qt.underlying_address
            WHERE rak.block_datetime + INTERVAL '72 hours' <= CURRENT_TIMESTAMP
            GROUP BY 1,2,3,4,5,6,7,8,9,10,11
        """.format(
            reserve_auction_table=self.models.reserve_auction._meta.db_table,
            reserve_auction_kick_table=self.models.reserve_auction_kick._meta.db_table,
            reserve_auction_take_table=self.models.reserve_auction_take._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
        )
        sql_vars = []
        return sql, sql_vars


class ReserveAuctionView(BaseChainView):
    def get(self, request, uid):
        sql_vars = [uid]
        sql = """
            SELECT
                  ra.uid
                , ra.pool_address
                , ra.claimable_reserves
                , ra.claimable_reserves_remaining
                , ra.last_take_price
                , ra.burn_epoch
                , ra.ajna_burned
                , rak.block_number
                , rak.kicker
                , rak.kicker_award
                , ct.symbol AS collateral_token_symbol
                , qt.symbol AS quote_token_symbol
                , COUNT(rat.order_index) as take_count
            FROM {reserve_auction_table} ra
            JOIN {reserve_auction_kick_table} rak
                ON rak.reserve_auction_uid = ra.uid
            LEFT JOIN {reserve_auction_take_table} rat
                ON rat.reserve_auction_uid = ra.uid
            JOIN {pool_table} p
                ON ra.pool_address = p.address
            JOIN {token_table} AS ct
                ON p.collateral_token_address = ct.underlying_address
            JOIN {token_table} AS qt
                ON p.quote_token_address = qt.underlying_address
            WHERE ra.uid = %s
            GROUP BY 1,2,3,4,5,6,7,8,9,10,11,12
        """.format(
            reserve_auction_table=self.models.reserve_auction._meta.db_table,
            reserve_auction_kick_table=self.models.reserve_auction_kick._meta.db_table,
            reserve_auction_take_table=self.models.reserve_auction_take._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
        )
        with connection.cursor() as cursor:
            cursor.execute(sql, sql_vars)
            data = fetch_one(cursor)

        if not data:
            raise Http404

        return Response(data, status.HTTP_200_OK)


class ReserveAuctionEventsView(RawSQLPaginatedChainView):
    default_order = "-order_index"

    def get_raw_sql(self, uid, **kwargs):
        sql = """
            SELECT
                  rat.order_index
                , 'Take' AS event
                , rat.reserve_auction_uid
                , rat.pool_address
                , rat.block_number
                , rat.block_datetime
                , rat.transaction_hash
                , jsonb_build_object(
                    'taker', rat.taker,
                    'claimable_reserves_remaining', rat.claimable_reserves_remaining::text,
                    'auction_price', rat.auction_price::text,
                    'ajna_burned', rat.ajna_burned::text,
                    'quote_purchased', rat.quote_purchased::text
                ) AS data
            FROM {reserve_auction_take_table} rat
            WHERE rat.reserve_auction_uid = %s

            UNION

            SELECT
                  rak.order_index
                , 'Kick' AS event
                , rak.reserve_auction_uid
                , rak.pool_address
                , rak.block_number
                , rak.block_datetime
                , rak.transaction_hash
                , jsonb_build_object(
                    'kicker', rak.kicker,
                    'kicker_award', rak.kicker_award::text,
                    'claimable_reserves', rak.claimable_reserves::text,
                    'starting_price', rak.starting_price::text
                ) AS data
            FROM {reserve_auction_kick_table} rak
            WHERE rak.reserve_auction_uid = %s

        """.format(
            reserve_auction_take_table=self.models.reserve_auction_take._meta.db_table,
            reserve_auction_kick_table=self.models.reserve_auction_kick._meta.db_table,
        )

        sql_vars = [uid] * 2
        return sql, sql_vars

    def serialize_data(self, data):
        for row in data:
            row["data"] = json.loads(row["data"])
        return data
