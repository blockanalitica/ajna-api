from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import connection

from ajna.utils.db import fetch_one
from ajna.v2.ethereum.chain import Ethereum
from ajna.v2.goerli.chain import Goerli
from ajna.v2.modules.events import _get_token_price
from ajna.v2.modules.pools import save_all_pools_volume_for_date


class Command(BaseCommand):
    def _fix_event_prices(self, chain):
        self.stdout.write("_fix_event_prices")
        event_names = [
            "DrawDebt",
            "RepayDebt",
            "DrawDebtNFT",
            "AddQuoteToken",
            "RemoveQuoteToken",
            "MoveQuoteToken",
            "AddCollateral",
            "RemoveCollateral",
            "Kick",
            "Take",
            "BucketTake",
            "Settle",
            "AuctionSettle",
        ]
        for pool in chain.pool.objects.all():
            events = chain.pool_event.objects.filter(
                name__in=event_names, pool_address=pool.address
            )
            for event in events:
                match event.name:
                    case "DrawDebt" | "RepayDebt" | "DrawDebtNFT":
                        event.collateral_token_price = _get_token_price(
                            chain, pool.collateral_token_address, event.block_datetime
                        )
                        event.quote_token_price = _get_token_price(
                            chain,
                            pool.quote_token_address,
                            event.block_datetime,
                        )
                    case "AddQuoteToken" | "RemoveQuoteToken" | "MoveQuoteToken":
                        event.quote_token_price = _get_token_price(
                            chain,
                            pool.quote_token_address,
                            event.block_datetime,
                        )
                    case "AddCollateral" | "RemoveCollateral":
                        event.collateral_token_price = _get_token_price(
                            chain,
                            pool.collateral_token_address,
                            event.block_datetime,
                        )
                    case "Kick" | "Take" | "BucketTake" | "Settle" | "AuctionSettle":
                        event.collateral_token_price = _get_token_price(
                            chain,
                            pool.collateral_token_address,
                            event.block_datetime,
                        )
                        event.quote_token_price = _get_token_price(
                            chain,
                            pool.quote_token_address,
                            event.block_datetime,
                        )
                event.save(
                    update_fields=["collateral_token_price", "quote_token_price"]
                )

    def _fix_volume_today(self, chain):
        self.stdout.write("_fix_volume_today")
        sql = """
            SELECT
                  pool_address
                , SUM(
                    CASE
                        WHEN name = 'AddCollateral' THEN
                            CAST(data->>'amount' AS NUMERIC) / 1e18 * collateral_token_price
                        WHEN name = 'RemoveCollateral' THEN
                            CAST(data->>'amount' AS NUMERIC) / 1e18 * collateral_token_price
                        WHEN name = 'AddQuoteToken' THEN
                            CAST(data->>'amount' AS NUMERIC) / 1e18 * quote_token_price
                        WHEN name = 'RemoveQuoteToken' THEN
                            CAST(data->>'amount' AS NUMERIC) / 1e18 * quote_token_price
                        WHEN name = 'DrawDebt' THEN
                            CAST(data->>'amountBorrowed' AS NUMERIC) / 1e18 * quote_token_price +
                            CAST(data->>'collateralPledged' AS NUMERIC) / 1e18 * collateral_token_price
                        WHEN name = 'DrawDebtNFT' THEN
                            CAST(data->>'amountBorrowed' AS NUMERIC) / 1e18 * quote_token_price
                        WHEN name = 'RepayDebt' THEN
                            CAST(data->>'quoteRepaid' AS NUMERIC) / 1e18 * quote_token_price +
                            CAST(data->>'collateralPulled' AS NUMERIC) / 1e18 * collateral_token_price
                    END
                  ) AS amount
                , ARRAY_AGG(name) as wat
            FROM {pool_event_table}
            WHERE block_datetime::DATE = %s
                AND block_datetime <= %s
                AND name IN (
                    'AddCollateral',
                    'RemoveCollateral',
                    'AddQuoteToken',
                    'RemoveQuoteToken',
                    'DrawDebt',
                    'DrawDebtNFT',
                    'RepayDebt'
                )
                AND pool_address = %s
            GROUP BY 1
        """.format(
            pool_event_table=chain.pool_event._meta.db_table
        )

        snapshots = chain.pool_snapshot.objects.all().order_by("address", "datetime")
        for snapshot in snapshots.iterator():
            dt = snapshot.datetime - timedelta(seconds=1)
            sql_vars = [dt.date(), dt, snapshot.address]
            with connection.cursor() as cursor:
                cursor.execute(sql, sql_vars)
                volume = fetch_one(cursor)
            if volume:
                snapshot.volume_today = volume["amount"]
                snapshot.save(update_fields=["volume_today"])

    def _fix_pool_volume_snapshot(self, chain):
        event = chain.pool_event.objects.all().order_by("block_datetime").first()

        dt = event.block_datetime.date()
        while dt <= date.today():
            save_all_pools_volume_for_date(chain, dt)
            dt += timedelta(days=1)

    def handle(self, *args, **options):
        goerli = Goerli()
        self._fix_event_prices(goerli)
        self._fix_volume_today(goerli)
        self._fix_pool_volume_snapshot(goerli)

        ethereum = Ethereum()
        self._fix_event_prices(ethereum)
        self._fix_volume_today(ethereum)
        self._fix_pool_volume_snapshot(ethereum)
