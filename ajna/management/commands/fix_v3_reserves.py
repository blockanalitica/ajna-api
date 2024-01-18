from decimal import Decimal

from django.core.management.base import BaseCommand

from ajna.v3.arbitrum.chain import Arbitrum
from ajna.v3.base.chain import Base
from ajna.v3.ethereum.chain import Ethereum
from ajna.v3.goerli.chain import Goerli
from ajna.v3.modules.positions import EventProcessor
from ajna.v3.optimism.chain import Optimism
from ajna.v3.polygon.chain import Polygon


class Command(BaseCommand):
    def handle(self, *args, **options):
        chains = [Ethereum, Goerli, Base, Polygon, Arbitrum, Optimism]

        for chain_cls in chains:
            chain = chain_cls()

            chain.pool.objects.all().update(total_ajna_burned=Decimal("0"))

            chain.reserve_auction.objects.all().delete()
            chain.reserve_auction_kick.objects.all().delete()
            chain.reserve_auction_take.objects.all().delete()

            events = chain.pool_event.objects.filter(
                name__in=["KickReserveAuction", "ReserveAuction"],
            ).order_by("order_index")

            processor = EventProcessor(chain)
            for event in events:
                processor._process_reserve_auctions(event)
