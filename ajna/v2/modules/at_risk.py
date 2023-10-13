import logging

log = logging.getLogger(__name__)

WALLETS_AT_RISK_SQL = """
    SELECT
          x.wallet_address
        , x.collateral
        , x.debt
        , x.collateral_usd
        , x.debt_usd
        , x.lup
        , x.collateral_token_symbol
        , x.quote_token_symbol
        , wt.last_activity
        , CASE
            WHEN (1 -  x.health_rate) < 0
            THEN ROUND(1 -  x.health_rate, 2)
            ELSE 0
        END AS price_change
    FROM (
        SELECT
              cwpt.wallet_address
            , cwpt.collateral
            , cwpt.t0debt * pt.pending_inflator AS debt
            , cwpt.collateral * ct.underlying_price AS collateral_usd
            , cwpt.t0debt * pt.pending_inflator * qt.underlying_price AS debt_usd
            , pt.lup
            , ct.symbol AS collateral_token_symbol
            , qt.symbol AS quote_token_symbol
            , CASE
                WHEN NULLIF(cwpt.collateral, 0) IS NULL
                    OR NULLIF(cwpt.t0debt, 0) IS NULL
                THEN NULL
                ELSE pt.lup / ((cwpt.t0debt * pt.pending_inflator) / cwpt.collateral)
              END AS health_rate
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
    WHERE ROUND(1 -  x.health_rate, 2) >= %s
"""
