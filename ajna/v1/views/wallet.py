from . import RawSQLPaginatedChainView


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

        return sql, sql_vars


class WalletPositionsView(RawSQLPaginatedChainView):
    order_nulls_last = True

    def get_raw_sql(self, wallet_address, search_filters, **kwargs):
        sql = """
            SELECT *
            FROM {current_position_table}
            WHERE wallet_address = %s
        """.format(
            current_position_table=self.models.current_wallet_position._meta.db_table,
        )
        sql_vars = [wallet_address]

        return sql, sql_vars


class WalletEventsView(RawSQLPaginatedChainView):
    def get_raw_sql(self, wallet_address, search_filters, **kwargs):
        sql_vars = [wallet_address]

        sql = """
            SELECT
                  e.name
                , e.data
                , e.pool_address
                , e.block_number
            FROM {pool_event_table} e
            WHERE e.wallet_addresses @> ARRAY[%s::varchar(42)]
            ORDER BY order_index DESC
        """.format(
            pool_event_table=self.models.pool_event._meta.db_table,
        )
        return sql, sql_vars
