from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand

from ajna.v4.modules.networks import save_network_stats_for_date
from ajna.v4.modules.pools import save_all_pools_volume_for_date
from ajna.v4.modules.prices import update_token_prices
from ajna.v4.rari.chain import Rari


class Command(BaseCommand):
    def handle(self, *args, **options):
        chain = Rari()

        update_token_prices(chain, chain.chain)

        chain.pool_snapshot.objects.filter(
            collateral_token_address="0x362fae9a75b27bbc550aac28a7c1f96c8d483120"  # noqa: S106
        ).update(collateral_token_price=Decimal("1"))

        chain.pool_snapshot.objects.filter(
            quote_token_address="0x362fae9a75b27bbc550aac28a7c1f96c8d483120"  # noqa: S106
        ).update(quote_token_price=Decimal("1"))

        start_date = date(2024, 12, 15)
        for x in range(3):
            for_date = start_date + timedelta(days=x)
            save_all_pools_volume_for_date(chain, for_date)
            save_network_stats_for_date(chain, for_date, "rari")

        # collateral pools
        for address in [
            "0x4555a9c49b560da0b914b44fe72b79d4375a12a1",
            "0xedc413cf600507e4c4ef06d79c921307bb1ecfd8",
        ]:
            chain.pool_event.objects.filter(pool_address=address).update(
                collateral_token_price=Decimal("1")
            )
        # quote pools
        for address in [
            "0x275f52176f4151a46f09ffa13e9990f7f544906a",
            "0x6bf50c09eeccfaf0be1843241ea8225598f66434",
        ]:
            chain.pool_event.objects.filter(pool_address=address).update(
                quote_token_price=Decimal("1")
            )
