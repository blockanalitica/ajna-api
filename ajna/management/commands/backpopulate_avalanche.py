from datetime import date, datetime, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand

from ajna.sources.defillama import fetch_price_for_timestamp
from ajna.utils.http import retry_get_json
from ajna.utils.utils import datetime_to_next_full_hour
from ajna.v4.avalanche.chain import Avalanche
from ajna.v4.modules.networks import save_network_stats_for_date
from ajna.v4.modules.pools import PoolERC20Manager
from ajna.v4.modules.prices import STABLECOIN_SYMBOLS

DEFILLAMA_CHAIN_NAME = "avax"
CHAIN_ID = "43114"
NETWORK = "avalanche"


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "api_key",
            type=str,
        )

    def _get_block_for_timestamp(self, timestamp):
        timestamp = int(timestamp)
        api_url = "https://api.etherscan.io/v2/api"

        url = (
            f"{api_url}?chainid={CHAIN_ID}&module=block&action=getblocknobytime"
            f"&timestamp={timestamp}&closest=before&apikey={self.api_key}"
        )
        data = retry_get_json(url)
        result = int(data["result"])
        return result

    def _get_token_info(self, token_address, dt):
        token = self.chain.token.objects.only("decimals", "underlying_price", "symbol").get(
            underlying_address=token_address
        )
        price_feed = self.chain.price_feed.objects.filter(
            underlying_address=token_address,
            datetime__date=dt.date(),
        ).latest()
        return {"decimals": token.decimals, "symbol": token.symbol, "price": price_feed.price}

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
            if symbol in STABLECOIN_SYMBOLS:
                self.chain.price_feed.objects.create(
                    underlying_address=token_address,
                    price=Decimal("1"),
                    datetime=dt,
                    timestamp=dt.timestamp(),
                    estimated=True,
                )
            else:
                coin = f"{DEFILLAMA_CHAIN_NAME}:{token_address}"
                if coin in price_mapping:
                    price = price_mapping[coin]["price"]
                    self.chain.price_feed.objects.create(
                        underlying_address=token_address,
                        price=price,
                        datetime=dt,
                        timestamp=dt.timestamp(),
                        estimated=False,
                    )

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

            self.chain.pool_snapshot.objects.update_or_create(
                address=pool.address,
                datetime=datetime_to_next_full_hour(dt),
                defaults=pool_data,
            )

    def handle(self, *args, **options):
        self.api_key = options["api_key"]

        deploy_dt = date(2024, 12, 17)

        self.chain = Avalanche()
        mngr = PoolERC20Manager(self.chain)

        for i in range(34):
            dt = datetime.combine(deploy_dt + timedelta(days=i), datetime.max.time())
            self.stdout.write(f"Starting backpopulate for date: {dt}")
            self._save_token_prices(dt)
            self._save_pool_snapshots(mngr, dt)

            save_network_stats_for_date(self.chain, dt.date(), NETWORK)
