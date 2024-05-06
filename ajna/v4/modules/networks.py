from datetime import date, timedelta
from decimal import Decimal

from ajna.utils.db import fetch_one

from ..models import V4NetworkStatsDaily


def save_network_stats_for_date(models, dt, network):
    if not isinstance(dt, date):
        raise TypeError

    sql = """
        SELECT
              SUM(x.tvl) AS tvl
            , SUM(x.collateral_usd) AS collateral_usd
            , SUM(x.supply_usd) AS supply_usd
            , SUM(x.debt_usd) AS debt_usd
        FROM (
            SELECT DISTINCT ON (DATE_TRUNC('day', ps.datetime), ps.address)
                  DATE_TRUNC('day', ps.datetime) AS date
                , COALESCE(ps.collateral_token_balance * ps.collateral_token_price, 0)
                  + COALESCE(quote_token_balance * ps.quote_token_price, 0) AS tvl
                , ps.pledged_collateral * ps.collateral_token_price AS collateral_usd
                , ps.pool_size * ps.quote_token_price AS supply_usd
                , ps.debt * ps.quote_token_price AS debt_usd
            FROM {pool_snapshot_table} ps
            WHERE ps.datetime >= %s
                AND ps.datetime < %s
            ORDER BY 1, ps.address, ps.datetime DESC
        ) x
    """.format(
        pool_snapshot_table=models.pool_snapshot._meta.db_table
    )
    sql_vars = [dt, dt + timedelta(days=1)]

    data = fetch_one(sql, sql_vars)

    V4NetworkStatsDaily.objects.update_or_create(
        network=network,
        date=dt,
        defaults={
            "tvl": data["tvl"] or Decimal("0"),
            "collateral_usd": data["collateral_usd"] or Decimal("0"),
            "supply_usd": data["supply_usd"] or Decimal("0"),
            "debt_usd": data["debt_usd"] or Decimal("0"),
        },
    )
