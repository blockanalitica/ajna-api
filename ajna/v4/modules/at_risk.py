import logging
from datetime import datetime, timedelta

from ajna.constants import MAX_INFLATED_PRICE
from ajna.utils.db import fetch_all

log = logging.getLogger(__name__)

WALLETS_AT_RISK_SQL = """
    SELECT
          x.wallet_address
        , x.pool_address
        , x.collateral
        , x.debt
        , x.collateral_usd
        , x.debt_usd
        , x.lup
        , x.collateral_token_symbol
        , x.quote_token_symbol
        , x.threshold_price
        , x.neutral_price
        , wt.last_activity
        , -ROUND(1 -  1 / x.health_rate, 4) AS price_change
    FROM (
        SELECT
              cwpt.wallet_address
            , cwpt.pool_address
            , cwpt.collateral
            , cwpt.t0debt * pt.pending_inflator AS debt
            , cwpt.collateral * ct.underlying_price AS collateral_usd
            , cwpt.t0debt * pt.pending_inflator * qt.underlying_price AS debt_usd
            , CASE
                WHEN NULLIF(cwpt.collateral, 0) IS NULL
                THEN NULL
                ELSE LEAST(
                    (cwpt.t0debt * pt.pending_inflator * 1.04) / cwpt.collateral * cwpt.np_tp_ratio,
                    %s
                )
              END AS neutral_price
            , pt.lup
            , ct.symbol AS collateral_token_symbol
            , qt.symbol AS quote_token_symbol
            , CASE
                WHEN NULLIF(cwpt.collateral, 0) IS NULL
                    OR NULLIF(cwpt.t0debt, 0) IS NULL
                THEN NULL
                ELSE pt.lup / ((cwpt.t0debt * pt.pending_inflator) / cwpt.collateral * 1.04)
              END AS health_rate
            , CASE
                WHEN NULLIF(cwpt.collateral, 0) IS NULL
                    OR NULLIF(cwpt.t0debt, 0) IS NULL
                THEN NULL
                ELSE (cwpt.t0debt * pt.pending_inflator) / cwpt.collateral * 1.04
              END AS threshold_price
        FROM {current_wallet_position_table} cwpt
        JOIN {pool_table} pt
            ON cwpt.pool_address = pt.address
        JOIN {token_table} AS ct
            ON pt.collateral_token_address = ct.underlying_address
        JOIN {token_table} AS qt
            ON pt.quote_token_address = qt.underlying_address
        WHERE (cwpt.t0debt > 0.0001 AND cwpt.collateral > 0.0001)
    ) x
    LEFT JOIN {wallet_table} wt
        ON x.wallet_address = wt.address
    WHERE -ROUND(1 -  1 / x.health_rate, 4) >= %s AND x.health_rate > 0.1
"""


def wallets_at_risk_notification(chain):
    sql_vars = [MAX_INFLATED_PRICE, 0]
    sql = WALLETS_AT_RISK_SQL.format(
        current_wallet_position_table=chain.current_wallet_position._meta.db_table,
        pool_table=chain.pool._meta.db_table,
        token_table=chain.token._meta.db_table,
        wallet_table=chain.wallet._meta.db_table,
    )

    data = fetch_all(sql, sql_vars)

    for row in data:
        notification, created = chain.notification.objects.get_or_create(
            key=row["wallet_address"],
            pool_address=row["pool_address"],
            defaults={
                "type": "WalletAtRisk",
                "data": row,
                "datetime": datetime.now(),
            },
        )
        if not created and datetime.now() >= notification.datetime + timedelta(days=1):
            notification.key = "{}_{}".format(
                notification.key, notification.datetime.timestamp()
            )
            notification.save()
            chain.notification.objects.create(
                key=row["wallet_address"],
                pool_address=row["pool_address"],
                type="WalletAtRisk",
                data=row,
                datetime=datetime.now(),
            )
