from collections import defaultdict
from decimal import Decimal

from django.urls import path
from psycopg2.sql import SQL, Identifier
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ajna.utils.db import fetch_all
from ajna.utils.views import DaysAgoMixin

from ..arbitrum.chain import ArbitrumModels
from ..base.chain import BaseModels
from ..ethereum.chain import EthereumModels
from ..models import V3NetworkStatsDaily
from ..optimism.chain import OptimismModels
from ..polygon.chain import PolygonModels


class OverallView(DaysAgoMixin, APIView):
    days_ago_required = False
    days_ago_default = 7
    days_ago_options = [1, 7, 30, 365]

    default_order = "-tvl"
    ordering_fields = ["tvl", "collateral_usd", "supply_usd", "debt_usd"]

    def _get_ordering(self, request):
        param = request.query_params.get("order")
        ordering_fields = []
        for field in self.ordering_fields:
            ordering_fields.append(field)
            ordering_fields.append("-{}".format(field))

        if param in ordering_fields:
            return param
        return self.default_order

    def get(self, request):
        sql_vars = {"days_ago_dt": self.days_ago_dt}

        name_map = {
            "ethereum": "Ethereum Mainnet",
            "arbitrum": "Arbitrum One",
            "base": "Base",
            "optimism": "Optimism",
            "polygon": "Polygon PoS",
        }
        chain_models_map = {
            "ethereum": EthereumModels(),
            "arbitrum": ArbitrumModels(),
            "base": BaseModels(),
            "optimism": OptimismModels(),
            "polygon": PolygonModels(),
        }
        prev_sqls = []
        selects = []
        for key, models in chain_models_map.items():
            prev_name = "{}_previous".format(key)
            prev_sqls.append(
                """
                {name} AS (
                    SELECT DISTINCT ON (ps.address)
                          ps.address
                        , ps.pledged_collateral
                        , ps.pool_size
                        , ps.t0debt
                        , ps.collateral_token_balance
                        , ps.quote_token_balance
                    FROM {pool_snapshot_table} ps
                    WHERE ps.datetime > (%(days_ago_dt)s - INTERVAL '7 DAY')
                        AND ps.datetime <= %(days_ago_dt)s
                    ORDER BY ps.address, ps.datetime DESC
                )
            """.format(
                    name=prev_name,
                    pool_snapshot_table=models.pool_snapshot._meta.db_table,
                )
            )

            selects.append(
                """
                SELECT
                      SUM(sub.tvl) AS tvl
                    , SUM(sub.collateral_usd) AS collateral_usd
                    , SUM(sub.supply_usd) AS supply_usd
                    , SUM(sub.debt_usd) AS debt_usd
                    , SUM(sub.prev_tvl) AS prev_tvl
                    , SUM(sub.prev_collateral_usd) AS prev_collateral_usd
                    , SUM(sub.prev_supply_usd) AS prev_supply_usd
                    , SUM(sub.prev_debt_usd) AS prev_debt_usd
                    , '{name}' AS network_name
                    , '{key}' AS network
                FROM (
                    SELECT
                          p.pledged_collateral * ct.underlying_price AS collateral_usd
                        , p.pool_size * qt.underlying_price AS supply_usd
                        , p.debt * qt.underlying_price AS debt_usd
                        , COALESCE(p.collateral_token_balance * ct.underlying_price, 0) +
                          COALESCE(p.quote_token_balance * qt.underlying_price, 0) AS tvl
                        , prev.pledged_collateral * ct.underlying_price AS prev_collateral_usd
                        , prev.pool_size * qt.underlying_price AS prev_supply_usd
                        , prev.t0debt * p.pending_inflator * qt.underlying_price  AS prev_debt_usd
                        , COALESCE(prev.collateral_token_balance * ct.underlying_price, 0) +
                            COALESCE(prev.quote_token_balance * qt.underlying_price, 0) AS prev_tvl
                    FROM {pool_table} AS p
                    JOIN {token_table} AS ct
                        ON p.collateral_token_address = ct.underlying_address
                    JOIN {token_table} AS qt
                        ON p.quote_token_address = qt.underlying_address
                    LEFT JOIN {prev_name} AS prev
                        ON prev.address = p.address
                ) AS sub
            """.format(
                    prev_name=prev_name,
                    name=name_map[key],
                    key=key,
                    token_table=models.token._meta.db_table,
                    pool_table=models.pool._meta.db_table,
                )
            )

        sql = """
            WITH {prev_sql}
            {selects}
        """.format(
            prev_sql=",".join(prev_sqls), selects=" UNION ".join(selects)
        )

        order = self._get_ordering(request)
        if order:
            if order.startswith("-"):
                sql = SQL("{} ORDER BY {} DESC").format(SQL(sql), Identifier(order[1:]))
            else:
                sql = SQL("{} ORDER BY {} ASC").format(SQL(sql), Identifier(order))

        data = fetch_all(sql, sql_vars)

        totals = defaultdict(Decimal)
        for row in data:
            totals["tvl"] += row["tvl"] or Decimal("0")
            totals["debt_usd"] += row["debt_usd"] or Decimal("0")
            totals["supply_usd"] += row["supply_usd"] or Decimal("0")
            totals["collateral_usd"] += row["collateral_usd"] or Decimal("0")
            totals["prev_tvl"] += row["prev_tvl"] or Decimal("0")
            totals["prev_debt_usd"] += row["prev_debt_usd"] or Decimal("0")
            totals["prev_supply_usd"] += row["prev_supply_usd"] or Decimal("0")
            totals["prev_collateral_usd"] += row["prev_collateral_usd"] or Decimal("0")

        return Response({"results": data, "totals": totals}, status.HTTP_200_OK)


class HistoricView(DaysAgoMixin, APIView):
    days_ago_required = False
    days_ago_default = 30
    days_ago_options = [30, 365]

    def get(self, request):
        sql = """
            SELECT
                  date
                , SUM(tvl) AS tvl
                , SUM(collateral_usd) AS collateral_usd
                , SUM(supply_usd) AS  supply_usd
                , SUM(debt_usd) AS debt_usd
            FROM {network_stats_daily_table}
            WHERE date >= %s
            GROUP BY 1
            ORDER BY date
        """.format(
            network_stats_daily_table=V3NetworkStatsDaily._meta.db_table
        )
        data = fetch_all(sql, [self.days_ago_dt])
        return Response(data, status.HTTP_200_OK)


urlpatterns = [
    path("", OverallView.as_view(), name="overall"),
    path("historic/", HistoricView.as_view(), name="historic"),
]
