import logging
from datetime import date, datetime, time, timedelta

from ajna.utils.db import fetch_one

log = logging.getLogger(__name__)


def sync_activity_snapshots(chain):
    last_snapshot = chain.activity_snapshot.objects.order_by("-date").first()
    if last_snapshot:
        last_date = last_snapshot.date
    else:
        first_wallet = chain.wallet.objects.order_by("first_activity").first()
        if first_wallet:
            last_date = first_wallet.first_activity.date()
        else:
            last_date = date.today()

    if last_date == date.today() and datetime.now().time() < time(0, 15):
        # If we're only doing snapshot for today, and current time is less than 15
        # minutes after midnight, also update yesterdays snapshots so that we
        # pick up all events that potentially happened between last run and midnight
        last_date = date.today() - timedelta(days=1)

    days = (date.today() - last_date).days
    for i in range(days + 1):
        dt = last_date + timedelta(days=i)
        log.debug(
            "Calling save_activity_snapshot_for_date with chain %s and date %s", chain.chain, dt
        )
        save_activity_snapshot_for_date(chain, dt)


def save_activity_snapshot_for_date(chain, dt):
    sql = f"""
        WITH active_wallets AS (
            SELECT
                COUNT(*) AS active_wallets
            FROM {chain.wallet_position._meta.db_table} wpt
            WHERE DATE(wpt.datetime) = %(dt)s
        ),
        total_wallets AS (
            SELECT
                COUNT(*) AS total_wallets
            FROM (
                SELECT DISTINCT wallet_address
                FROM {chain.wallet_position._meta.db_table} wpt
                WHERE DATE(wpt.datetime) <= %(dt)s
            ) d
        ),
        active_this_month AS (
            SELECT
                COUNT(*) AS active_this_month
            FROM (
                SELECT DISTINCT wallet_address
                FROM {chain.wallet_position._meta.db_table} wpt
                WHERE wpt.datetime >= DATE_TRUNC('month', %(dt)s)
                    AND wpt.datetime <= %(dt)s
            ) d
        ),
        new_this_month AS (
            SELECT
                COUNT(*) AS new_this_month
            FROM {chain.wallet._meta.db_table} wpt
            WHERE wpt.first_activity >= DATE_TRUNC('month', %(dt)s)
                AND wpt.first_activity <= %(dt)s
        ),
        new_wallets AS (
            SELECT
                COUNT(*) AS new_wallets
            FROM {chain.wallet._meta.db_table} wt
            WHERE DATE(wt.first_activity) = %(dt)s
        )

        SELECT
            *
        FROM active_wallets
        LEFT JOIN total_wallets ON 1=1
        LEFT JOIN new_wallets ON 1=1
        LEFT JOIN active_this_month ON 1=1
        LEFT JOIN new_this_month ON 1=1
    """

    data = fetch_one(sql, {"dt": dt})
    chain.activity_snapshot.objects.update_or_create(
        date=dt,
        defaults={
            "active_wallets": data["active_wallets"],
            "total_wallets": data["total_wallets"],
            "new_wallets": data["new_wallets"],
            "active_this_month": data["active_this_month"],
            "new_this_month": data["new_this_month"],
        },
    )
