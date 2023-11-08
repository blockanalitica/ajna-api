from django.core.management.base import BaseCommand

from ajna.v2.ethereum.chain import Ethereum
from ajna.v2.goerli.chain import Goerli
from ajna.v2.modules.positions import EventProcessor


class Command(BaseCommand):
    def _do_work(self, chain):
        chain.notification.objects.all().delete()
        events = chain.pool_event.objects.filter(
            name__in=[
                "AddQuoteToken",
                "DrawDebt",
                "AddCollateral",
                "Kick",
                "AuctionSettle",
            ]
        ).order_by("order_index")

        p = EventProcessor(chain)
        for event in events:
            p._create_notifications(event)

    def handle(self, *args, **options):
        goerli = Goerli()
        self._do_work(goerli)

        eth = Ethereum()
        self._do_work(eth)
