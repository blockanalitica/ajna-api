import csv
from datetime import datetime, timedelta
from decimal import Decimal

from django.db import connection
from django.http import Http404, HttpResponse
from rest_framework import status
from rest_framework.response import Response

from ajna.utils.db import fetch_all, fetch_one

from . import BaseChainView, RawSQLPaginatedChainView


class PoolEventsView(RawSQLPaginatedChainView):
    def get_raw_sql(self, pool_address, search_filters, **kwargs):
        sql = """
            SELECT *
            FROM {pool_event_table}
            WHERE pool_address = %s
        """.format(
            pool_event_table=self.models.pool_event._meta.db_table,
        )
        sql_vars = [pool_address]
        print(sql_vars)

        return sql, sql_vars


class WalletPositionsView(RawSQLPaginatedChainView):
    order_nulls_last = True

    def get_raw_sql(self, wallet_address, search_filters, **kwargs):
        sql = """
            SELECT *
            FROM {current_position_table}
            WHERE wallet_address = %s
        """.format(
            current_position_table=self.models.current_position._meta.db_table,
        )
        sql_vars = [wallet_address]

        return sql, sql_vars


class WalletEventsView(RawSQLPaginatedChainView):
    order_nulls_last = True
    default_order = "-block_timestamp"
    ordering_fields = ["block_timestamp", "amount", "collateral", "account"]

    def _get_sql_add_collateral(self):
        return """
            SELECT
                CONCAT('add_collateral', id) AS id
                , 'add_collateral' AS event_type
                , amount
                , '{collateral_symbol}' AS amount_symbol
                , CAST(NULL AS numeric) AS collateral
                , NULL AS collateral_symbol
                , actor AS account
                , block_number
                , block_timestamp
                , transaction_hash
                , CAST(NULL AS numeric) AS bucket_index_from
                , CAST(NULL AS numeric) AS bucket_index_to
                , pool_address
            FROM {add_collateral_table}
            WHERE actor = %s AND block_timestamp >= %s
        """.format(
            add_collateral_table=self.models.add_collateral._meta.db_table,
            collateral_symbol="X",
        )

    def _get_sql_remove_collateral(self):
        return """
            SELECT
                CONCAT('remove_collateral', id) AS id
                , 'remove_collateral' AS event_type
                , amount
                , '{collateral_symbol}' AS amount_symbol
                , CAST(NULL AS numeric) AS collateral
                , NULL AS collateral_symbol
                , claimer AS account
                , block_number
                , block_timestamp
                , transaction_hash
                , CAST(NULL AS numeric) AS bucket_index_from
                , CAST(NULL AS numeric) AS bucket_index_to
                , pool_address
            FROM {remove_collateral_table}
            WHERE claimer = %s AND block_timestamp >= %s
        """.format(
            remove_collateral_table=self.models.remove_collateral._meta.db_table,
            collateral_symbol="X",
        )

    def _get_sql_add_quote_token(self):
        return """
            SELECT
                CONCAT('add_quote_token', id) AS id
                , 'add_quote_token' AS event_type
                , amount
                , '{quote_symbol}' AS amount_symbol
                , CAST(NULL AS numeric) AS collateral
                , NULL AS collateral_symbol
                , lender AS account
                , block_number
                , block_timestamp
                , transaction_hash
                , CAST(NULL AS numeric) AS bucket_index_from
                , CAST(NULL AS numeric) AS bucket_index_to
                , pool_address
            FROM {add_quote_token_table}
            WHERE lender = %s AND block_timestamp >= %s
        """.format(
            add_quote_token_table=self.models.add_quote_token._meta.db_table,
            quote_symbol="Y",
        )

    def _get_sql_remove_quote_token(self):
        return """
            SELECT
                CONCAT('remove_quote_token', id) AS id
                , 'remove_quote_token' AS event_type
                , amount
                , '{quote_symbol}' AS amount_symbol
                , CAST(NULL AS numeric) AS collateral
                , NULL AS collateral_symbol
                , lender AS account
                , block_number
                , block_timestamp
                , transaction_hash
                , CAST(NULL AS numeric) AS bucket_index_from
                , CAST(NULL AS numeric) AS bucket_index_to
                , pool_address
            FROM {remove_quote_token_table}
            WHERE lender = %s AND block_timestamp >= %s
        """.format(
            remove_quote_token_table=self.models.remove_quote_token._meta.db_table,
            quote_symbol="Y",
        )

    def _get_sql_move_quote_token(self):
        return """
            SELECT
                CONCAT('move_quote_token', id) AS id
                , 'move_quote_token' AS event_type
                , amount
                , '{quote_symbol}' AS amount_symbol
                , CAST(NULL AS numeric) AS collateral
                , NULL AS collateral_symbol
                , lender AS account
                , block_number
                , block_timestamp
                , transaction_hash
                , bucket_index_from
                , bucket_index_to
                , pool_address
            FROM {remove_quote_token_table}
            WHERE lender = %s AND block_timestamp >= %s
        """.format(
            remove_quote_token_table=self.models.move_quote_token._meta.db_table,
            quote_symbol="Y",
        )

    def _get_sql_draw_debt(self):
        return """
            SELECT
                CONCAT('draw_debt', id) AS id
                , 'draw_debt' AS event_type
                , amount_borrowed AS amount
                , '{quote_symbol}' AS amount_symbol
                , collateral_pledged AS collateral
                , '{collateral_symbol}' AS collateral_symbol
                , borrower AS account
                , block_number
                , block_timestamp
                , transaction_hash
                , CAST(NULL AS numeric) AS bucket_index_from
                , CAST(NULL AS numeric) AS bucket_index_to
                , pool_address
            FROM {draw_debt_table}
            WHERE borrower = %s AND block_timestamp >= %s
        """.format(
            draw_debt_table=self.models.draw_debt._meta.db_table,
            quote_symbol="Y",
            collateral_symbol="X",
        )

    def _get_sql_repay_debt(self):
        return """
            SELECT
                CONCAT('repay_debt', id) AS id
                , 'repay_debt' AS event_type
                , quote_repaid AS amount
                , '{quote_symbol}' AS amount_symbol
                , collateral_pulled AS collateral
                , '{collateral_symbol}' AS collateral_symbol
                , borrower AS account
                , block_number
                , block_timestamp
                , transaction_hash
                , CAST(NULL AS numeric) AS bucket_index_from
                , CAST(NULL AS numeric) AS bucket_index_to
                , pool_address
            FROM {repay_debt_table}
            WHERE borrower = %s AND block_timestamp >= %s
        """.format(
            repay_debt_table=self.models.repay_debt._meta.db_table,
            quote_symbol="Y",
            collateral_symbol="X",
        )

    def get_raw_sql(self, wallet_address, search_filters, **kwargs):
        event_type = ""
        # TODO: change this to a reasonable number (perhaps 1 day or something like that)
        timestamp = (datetime.now() - timedelta(days=365)).timestamp()

        sql_vars = [wallet_address, timestamp]

        match event_type:
            case "add_collateral":
                sql = self._get_sql_add_collateral()
            case "remove_collateral":
                sql = self._get_sql_remove_collateral()
            case "add_quote_token":
                sql = self._get_sql_add_quote_token()
            case "move_quote_token":
                sql = self._get_sql_move_quote_token()
            case "remove_quote_token":
                sql = self._get_sql_remove_quote_token()
            case "draw_debt":
                sql = self._get_sql_draw_debt()
            case "repay_debt":
                sql = self._get_sql_repay_debt()
            case _:
                sql = " UNION ".join(
                    [
                        self._get_sql_add_collateral(),
                        self._get_sql_remove_collateral(),
                        self._get_sql_add_quote_token(),
                        self._get_sql_move_quote_token(),
                        self._get_sql_remove_quote_token(),
                        self._get_sql_draw_debt(),
                        self._get_sql_repay_debt(),
                    ]
                )
                sql_vars = [wallet_address, timestamp] * 7

        return sql, sql_vars
