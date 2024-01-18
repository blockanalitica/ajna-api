from decimal import Decimal

from django.core.management.base import BaseCommand

from ajna.v2.ethereum.chain import Ethereum
from ajna.v2.modules.positions import EventProcessor


class Command(BaseCommand):
    def handle(self, *args, **options):
        chain = Ethereum()

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
