from rest_framework import status
from rest_framework.response import Response

from ajna.utils.db import fetch_all, fetch_one
from ajna.utils.views import BaseChainView


class ActivityView(BaseChainView):
    days_ago_required = False
    days_ago_default = 1
    days_ago_options = [1, 7, 30, 90, 365, 9999]

    def get(self, request):
        sql = f"""
            WITH previous AS (
                SELECT
                    ast.total_wallets
                FROM {self.chain.activity_snapshot._meta.db_table} ast
                WHERE ast.date = %s
            )

            SELECT
                  ast.active_wallets
                , ast.total_wallets
                , ast.new_wallets
                , ast.active_this_month
                , ast.new_this_month
                , prev.total_wallets AS prev_total_wallets
            FROM {self.chain.activity_snapshot._meta.db_table} ast
            LEFT JOIN previous AS prev ON 1 = 1
            ORDER BY ast.date DESC
            LIMIT 1
        """
        data = fetch_one(sql, [self.days_ago_dt.date()])
        return Response(data, status.HTTP_200_OK)


class ActivityHistoricView(BaseChainView):
    days_ago_required = False
    days_ago_default = 30
    days_ago_options = [30, 90, 365, 9999]

    def get(self, request):
        if self.days_ago > 30:
            sql = f"""
                SELECT
                      latest.dt AS date
                    , a.active_this_month AS active
                    , a.new_this_month AS new
                    , a.total_wallets AS total
                FROM {self.chain.activity_snapshot._meta.db_table} a
                JOIN (
                    SELECT
                          DATE_TRUNC('month', ast.date) AS dt
                        , MAX(ast.date) AS max_datetime
                    FROM {self.chain.activity_snapshot._meta.db_table} ast
                    WHERE ast.date >= %s
                    GROUP BY 1
                ) latest
                ON a.date = latest.max_datetime
                ORDER BY 1
            """
            data = fetch_all(sql, [self.days_ago_dt.date()])
        else:
            sql = f"""
                SELECT
                      ast.date
                    , ast.active_wallets AS active
                    , ast.total_wallets AS total
                    , ast.new_wallets AS new
                FROM {self.chain.activity_snapshot._meta.db_table} ast
                WHERE ast.date >= %s
                ORDER BY ast.date
            """
            data = fetch_all(sql, [self.days_ago_dt.date()])

        return Response(data, status.HTTP_200_OK)
