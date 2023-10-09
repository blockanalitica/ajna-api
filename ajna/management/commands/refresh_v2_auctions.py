from django.core.management.base import BaseCommand

from ajna.v2.ethereum.chain import Ethereum
from ajna.v2.goerli.chain import Goerli
from ajna.v2.modules.auctions import (
    process_auction_settle_event,
    process_bucket_take_event,
    process_kick_event,
    process_settle_event,
    process_take_event,
)


class Command(BaseCommand):
    def _do_work(self, chain):
        chain.auction.objects.all().delete()
        chain.auction_kick.objects.all().delete()
        chain.auction_take.objects.all().delete()
        chain.auction_bucket_take.objects.all().delete()
        chain.auction_settle.objects.all().delete()
        chain.auction_auction_settle.objects.all().delete()

        event_names = ["Kick", "Take", "BucketTake", "Settle", "AuctionSettle"]

        events = chain.pool_event.objects.filter(name__in=event_names).order_by(
            "order_index"
        )

        for event in events:
            match event.name:
                case "Kick":
                    process_kick_event(chain, event)
                case "Take":
                    process_take_event(chain, event)
                case "BucketTake":
                    process_bucket_take_event(chain, event)
                case "Settle":
                    process_settle_event(chain, event)
                case "AuctionSettle":
                    process_auction_settle_event(chain, event)

    def handle(self, *args, **options):
        goerli = Goerli()
        self._do_work(goerli)

        ethereum = Ethereum()
        self._do_work(ethereum)
