from . import RawSQLPaginatedChainView


class PositionsView(RawSQLPaginatedChainView):
    order_nulls_last = True

    def get_raw_sql(self, search_filters, **kwargs):
        sql = """
            SELECT *
            FROM {current_position_table}
        """.format(
            current_position_table=self.models.current_position._meta.db_table,
        )

        sql_vars = []

        return sql, sql_vars
