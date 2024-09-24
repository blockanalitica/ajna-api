from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from ajna.utils.utils import datetime_to_next_full_hour
from ajna.v4.modules.pools import PoolERC20Manager
from ajna.v4.rari.chain import Rari


class Command(BaseCommand):
    def handle(self, *args, **options):
        dts = [
            [datetime(2024, 9, 19, 1, 2, 25), 471913],
            [datetime(2024, 9, 19, 13, 4, 55), 471950],
            [datetime(2024, 9, 20, 0, 35, 15), 471999],
            [datetime(2024, 9, 20, 13, 25, 28), 472699],
            [datetime(2024, 9, 21, 1, 20, 10), 478999],
            [datetime(2024, 9, 21, 12, 55, 16), 489999],
            [datetime(2024, 9, 22, 1, 54, 16), 495499],
            [datetime(2024, 9, 22, 12, 50, 56), 501499],
            [datetime(2024, 9, 23, 1, 51, 22), 504999],
            [datetime(2024, 9, 23, 14, 35, 4), 510066],
            [datetime(2024, 9, 24, 2, 1, 51), 512499],
            [datetime(2024, 9, 24, 13, 25, 30), 516466],
        ]

        chain = Rari()
        mngr = PoolERC20Manager(chain)

        address = "0x26ac6b64b2734b821a612db68a07d54d24459dd4".lower()
        pool = chain.pool.objects.get(address=address)

        for dt, block_number in dts:
            self.stdout.write(f"Working: {dt}")

            pools_data = mngr._fetch_pools_data([address], block_number=block_number)
            pool_data = pools_data[address]

            pool_data["volume_today"] = mngr._calculate_volume_for_pool_for_date(address, dt.date())

            collateral_token = mngr.token_info(pool.collateral_token_address)
            quote_token = mngr.token_info(pool.quote_token_address)

            # Add fields that we need for pool snapshot
            pool_data["collateral_token_price"] = collateral_token["price"]
            pool_data["quote_token_price"] = quote_token["price"]
            # total_ajna_burned is updated async in another task, so for snapshot
            # we need to fetch it from pool
            pool_data["total_ajna_burned"] = pool.total_ajna_burned

            collateralization = None
            if (
                pool_data["t0debt"] > 0
                and pool_data["pending_inflator"] > 0
                and quote_token["price"]
                and collateral_token["price"]
            ):
                collateralization = (
                    pool_data["pledged_collateral"] * collateral_token["price"]
                ) / (pool_data["t0debt"] * pool_data["pending_inflator"] * quote_token["price"])

            pool_data["collateralization"] = collateralization

            chain.pool_snapshot.objects.update_or_create(
                address=address,
                datetime=datetime_to_next_full_hour(dt),
                defaults=pool_data,
            )

            dt = dt + timedelta(hours=12)
