from django.http import Http404
from rest_framework import status
from rest_framework.response import Response

from ajna.utils.db import fetch_all, fetch_one
from ajna.utils.views import BaseChainView


class OverviewView(BaseChainView):
    days_ago_required = False
    days_ago_default = 1
    days_ago_options = [1, 7, 30, 90, 9999]

    def get(self, request):
        sql_vars = {"days_ago_dt": self.days_ago_dt}
        sql = """
            WITH previous AS (
                SELECT DISTINCT ON (ps.address)
                      ps.address
                    , ps.total_ajna_burned
                    , ps.pledged_collateral * ps.collateral_token_price AS pledged_collateral_usd
                    , ps.collateral_token_balance * ps.collateral_token_price AS collateral_usd
                    , ps.pool_size * ps.quote_token_price AS pool_size_usd
                    , ps.debt * ps.quote_token_price  AS debt_usd
                    , COALESCE(ps.collateral_token_balance * ps.collateral_token_price, 0) +
                        COALESCE(ps.quote_token_balance * ps.quote_token_price, 0) AS tvl
                FROM {pool_snapshot_table} ps
                WHERE ps.datetime > (%(days_ago_dt)s - INTERVAL '7 DAY')
                    AND ps.datetime <= %(days_ago_dt)s
                ORDER BY ps.address, ps.datetime DESC
            )

            SELECT
                  SUM(sub.tvl) AS total_tvl
                , SUM(sub.pledged_collateral * sub.collateral_token_underlying_price)
                  AS total_pledged_collateral
                , SUM(sub.collateral_token_balance * sub.collateral_token_underlying_price)
                  AS total_collateral
                , SUM(sub.pool_size * sub.quote_token_underlying_price) AS total_pool_size
                , SUM(sub.debt * sub.quote_token_underlying_price) AS total_current_debt
                , SUM(sub.total_ajna_burned) AS total_ajna_burned
                , SUM(sub.prev_tvl) AS prev_total_tvl
                , SUM(sub.prev_collateral_usd) AS prev_total_collateral
                , SUM(sub.prev_pledged_collateral_usd) AS prev_total_pledged_collateral
                , SUM(sub.prev_pool_size_usd) AS prev_total_pool_size
                , SUM(sub.prev_debt_usd) AS prev_total_current_debt
                , SUM(sub.prev_total_ajna_burned) AS prev_total_ajna_burned
            FROM (
                SELECT
                      pool.pledged_collateral
                    , pool.collateral_token_balance
                    , pool.pool_size
                    , pool.debt
                    , pool.total_ajna_burned
                    , ct.underlying_price AS collateral_token_underlying_price
                    , qt.underlying_price AS quote_token_underlying_price
                    , COALESCE(pool.collateral_token_balance * ct.underlying_price, 0) +
                      COALESCE(pool.quote_token_balance * qt.underlying_price, 0) AS tvl
                    , prev.pledged_collateral_usd AS prev_pledged_collateral_usd
                    , prev.collateral_usd AS prev_collateral_usd
                    , prev.pool_size_usd AS prev_pool_size_usd
                    , prev.debt_usd AS prev_debt_usd
                    , prev.tvl AS prev_tvl
                    , prev.total_ajna_burned AS prev_total_ajna_burned
                FROM {pool_table} AS pool
                JOIN {token_table} AS ct
                    ON pool.collateral_token_address = ct.underlying_address
                JOIN {token_table} AS qt
                    ON pool.quote_token_address = qt.underlying_address
                FULL JOIN previous AS prev
                    ON prev.address = pool.address
            ) AS sub
        """.format(
            token_table=self.models.token._meta.db_table,
            pool_table=self.models.pool._meta.db_table,
            pool_snapshot_table=self.models.pool_snapshot._meta.db_table,
        )

        data = fetch_one(sql, sql_vars)

        if not data:
            raise Http404

        return Response({"results": data}, status.HTTP_200_OK)


class HistoryView(BaseChainView):
    days_ago_required = False
    days_ago_default = 30
    days_ago_options = [30, 90, 9999]

    def _get_from_snapshot(self, amount_select):
        sql_vars = []
        days_ago_filter = ""
        if self.days_ago != 9999:
            days_ago_filter = "WHERE pst.datetime >= %s"
            sql_vars.append(self.days_ago_dt)

        sql = """
            SELECT
                  latest.dt
                , {amount_select}
            FROM {pool_snapshot_table} ps
            JOIN (
                SELECT
                      DATE(pst.datetime) AS dt
                    , pst.address
                    , MAX(pst.datetime) AS max_datetime
                FROM {pool_snapshot_table} pst
                {days_ago_filter}
                GROUP BY 1,2
            ) latest
            ON DATE(ps.datetime) = latest.dt
                AND ps.address = latest.address
                AND ps.datetime = latest.max_datetime
            GROUP BY 1
            ORDER BY 1
        """.format(
            pool_snapshot_table=self.models.pool_snapshot._meta.db_table,
            days_ago_filter=days_ago_filter,
            amount_select=amount_select,
        )
        return sql, sql_vars

    def _get_volume(self):
        sql = """
            SELECT
                  pvs.date AS dt
                , SUM(pvs.amount) AS amount
            FROM {pool_volume_snapshot_table} pvs
            WHERE pvs.date >= %s
            GROUP BY pvs.date
            ORDER BY pvs.date
        """.format(
            pool_volume_snapshot_table=self.models.pool_volume_snapshot._meta.db_table,
        )
        return sql, [self.days_ago_dt]

    def get(self, request):
        history_type = request.GET.get("type")

        match history_type:
            case "pledged_collateral":
                amount_select = "SUM(ps.pledged_collateral * ps.collateral_token_price) AS amount"
                sql, sql_vars = self._get_from_snapshot(amount_select)
            case "collateral":
                amount_select = (
                    "SUM(ps.collateral_token_balance * ps.collateral_token_price) AS amount"
                )
                sql, sql_vars = self._get_from_snapshot(amount_select)
            case "debt":
                amount_select = "SUM(ps.debt * ps.quote_token_price) AS amount"
                sql, sql_vars = self._get_from_snapshot(amount_select)
            case "tvl":
                amount_select = (
                    "SUM(COALESCE(ps.collateral_token_balance * ps.collateral_token_price, 0) "
                    "+ COALESCE(ps.quote_token_balance * ps.quote_token_price, 0)) AS amount"
                )
                sql, sql_vars = self._get_from_snapshot(amount_select)
            case "volume":
                sql, sql_vars = self._get_volume()
            case _:  # deposit or default
                amount_select = "SUM(ps.pool_size * ps.quote_token_price) AS amount"
                sql, sql_vars = self._get_from_snapshot(amount_select)

        data = fetch_all(sql, sql_vars)
        return Response(data, status.HTTP_200_OK)
