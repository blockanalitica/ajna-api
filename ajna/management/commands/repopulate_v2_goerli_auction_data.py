from django.core.management.base import BaseCommand

from ajna.v2.goerli.chain import Goerli
from ajna.v2.modules.positions import EventProcessor


class Command(BaseCommand):
    def handle(self, *args, **options):
        chain = Goerli()

        chain.auction.objects.all().delete()
        chain.auction_kick.objects.all().delete()
        chain.auction_take.objects.all().delete()
        chain.auction_bucket_take.objects.all().delete()
        chain.auction_settle.objects.all().delete()
        chain.auction_auction_settle.objects.all().delete()
        chain.auction_auction_nft_settle.objects.all().delete()

        processor = EventProcessor(chain)

        events = chain.pool_event.objects.filter(
            name__in=[
                "Kick",
                "Take",
                "BucketTake",
                "Settle",
                "AuctionSettle",
                "AuctionNFTSettle",
            ]
        ).order_by("order_index")
        for event in events:
            processor._process_auctions(event)
