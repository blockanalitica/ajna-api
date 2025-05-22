from datetime import date, datetime, timedelta

from django.core.management.base import BaseCommand

from ajna.sources.defillama import fetch_price_for_timestamp
from ajna.utils.http import retry_get_json
from ajna.utils.utils import datetime_to_next_full_hour
from ajna.v4.hemi.chain import Hemi
from ajna.v4.modules.networks import save_network_stats_for_date
from ajna.v4.modules.pools import PoolERC20Manager
from ajna.v4.modules.prices import _estimate_price_from_pools_for_token

DEFILLAMA_CHAIN_NAME = "hemi"
NETWORK = "hemi"


class Command(BaseCommand):
    def _save_token_prices(self, dt):
        tokens = self.chain.token.objects.all().values_list("underlying_address", "symbol")
        if not tokens:
            return

        underlying_addresses = [token[0] for token in tokens]

        coins = []
        for address in underlying_addresses:
            coins.append(f"{DEFILLAMA_CHAIN_NAME}:{address}")

        price_mapping = fetch_price_for_timestamp(int(dt.timestamp()), coins)
        for token_address, symbol in tokens:
            coin = f"{DEFILLAMA_CHAIN_NAME}:{token_address}"
            if coin in price_mapping:
                price = price_mapping[coin]["price"]
                self.chain.price_feed.objects.update_or_create(
                    underlying_address=token_address,
                    timestamp=dt.timestamp(),
                    defaults={
                        "price": price,
                        "datetime": dt,
                        "estimated": False,
                    },
                )
            else:
                # NOTE: this is not correct, but we only have one token where this will be
                # applicable and the only events are in the same day so we should be able
                # to get away with doing this
                price = _estimate_price_from_pools_for_token(self.chain, token_address, symbol)
                if price:
                    self.chain.price_feed.objects.update_or_create(
                        underlying_address=token_address,
                        timestamp=dt.timestamp(),
                        defaults={
                            "price": price,
                            "datetime": dt,
                            "estimated": True,
                        },
                    )

    def _get_block_for_timestamp(self, timestamp):
        timestamp = int(timestamp)
        api_url = "https://explorer.hemi.xyz/api"

        params = {
            "module": "block",
            "action": "getblocknobytime",
            "timestamp": timestamp,
            "closest": "before",
        }
        data = retry_get_json(api_url, params=params)
        result = int(data["result"]["blockNumber"])
        return result

    def _get_token_info(self, token_address, dt):
        token = self.chain.token.objects.only("decimals", "underlying_price", "symbol").get(
            underlying_address=token_address
        )

        try:
            price_feed = self.chain.price_feed.objects.filter(
                underlying_address=token_address,
                datetime__date=dt.date(),
            ).latest()
            price = price_feed.price
        except self.chain.price_feed.DoesNotExist:
            price = None

        return {"decimals": token.decimals, "symbol": token.symbol, "price": price}

    def _save_pool_snapshots(self, mngr, dt):
        block_number = self._get_block_for_timestamp(dt.timestamp())
        pools = self.chain.pool.objects.filter(created_at_block_number__lt=block_number)
        for pool in pools:
            pools_data = mngr._fetch_pools_data([pool.address], block_number=block_number)
            pool_data = pools_data[pool.address]

            pool_data["volume_today"] = mngr._calculate_volume_for_pool_for_date(
                pool.address, dt.date()
            )

            collateral_token = self._get_token_info(pool.collateral_token_address, dt)
            quote_token = self._get_token_info(pool.quote_token_address, dt)

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

            snap_dt = dt.replace(second=0, microsecond=0, minute=0, hour=dt.hour)
            if snap_dt.date() == date.today():
                snap_dt = datetime_to_next_full_hour(datetime.now())
            self.chain.pool_snapshot.objects.update_or_create(
                address=pool.address,
                datetime=snap_dt,
                defaults=pool_data,
            )

    def handle(self, *args, **options):
        deploy_dt = date(2025, 3, 5)

        self.chain = Hemi()
        mngr = PoolERC20Manager(self.chain)

        days = (date.today() - deploy_dt).days
        for i in range(days + 1):
            dt = datetime.combine(deploy_dt + timedelta(days=i), datetime.max.time())
            self.stdout.write(f"Starting backpopulate for date: {dt}")
            self._save_token_prices(dt)
            self._save_pool_snapshots(mngr, dt)

            save_network_stats_for_date(self.chain, dt.date(), NETWORK)
