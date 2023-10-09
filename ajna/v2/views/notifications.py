import json

from ajna.utils.views import RawSQLPaginatedChainView


class NotificationsView(RawSQLPaginatedChainView):
    default_order = "-datetime"

    def get_raw_sql(self, **kwargs):
        sql = """
            SELECT
                  nt.type
                , nt.key
                , nt.data
                , nt.datetime
                , nt.pool_address
                , ct.symbol AS collateral_token_symbol
                , qt.symbol AS quote_token_symbol
            FROM {notification_table} nt
            JOIN {pool_table} p
                ON nt.pool_address = p.address
            JOIN {token_table} AS ct
                ON p.collateral_token_address = ct.underlying_address
            JOIN {token_table} AS qt
                ON p.quote_token_address = qt.underlying_address
        """.format(
            notification_table=self.models.notification._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            token_table=self.models.token._meta.db_table,
        )
        sql_vars = []
        return sql, sql_vars

    def serialize_data(self, data):
        for row in data:
            if row["data"]:
                row["data"] = json.loads(row["data"])
        return data
