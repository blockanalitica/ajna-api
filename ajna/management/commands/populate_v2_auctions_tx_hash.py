from django.core.management.base import BaseCommand

from ajna.v2.ethereum.chain import Ethereum


class Command(BaseCommand):
    def populate_tx_hash(self, chain):
        for auction_kick in chain.auction_kick.objects.filter(
            transaction_hash__isnull=True
        ):
            tx_hash = chain.pool_event.objects.get(order_index=auction_kick.order_index)
            auction_kick.transaction_hash = tx_hash.transaction_hash
            auction_kick.save()

        for auction_take in chain.auction_take.objects.filter(
            transaction_hash__isnull=True
        ):
            tx_hash = chain.pool_event.objects.get(order_index=auction_take.order_index)
            auction_take.transaction_hash = tx_hash.transaction_hash
            auction_take.save()

        for auction_bucket_take in chain.auction_bucket_take.objects.filter(
            transaction_hash__isnull=True
        ):
            tx_hash = chain.pool_event.objects.get(
                order_index=auction_bucket_take.order_index
            )
            auction_bucket_take.transaction_hash = tx_hash.transaction_hash
            auction_bucket_take.save()

        for auction_settle in chain.auction_settle.objects.filter(
            transaction_hash__isnull=True
        ):
            tx_hash = chain.pool_event.objects.get(
                order_index=auction_settle.order_index
            )
            auction_settle.transaction_hash = tx_hash.transaction_hash
            auction_settle.save()

        for auction_auction_settle in chain.auction_auction_settle.objects.filter(
            transaction_hash__isnull=True
        ):
            tx_hash = chain.pool_event.objects.get(
                order_index=auction_auction_settle.order_index
            )
            auction_auction_settle.transaction_hash = tx_hash.transaction_hash
            auction_auction_settle.save()

        for (
            auction_auction_nft_settle
        ) in chain.auction_auction_nft_settle.objects.filter(
            transaction_hash__isnull=True
        ):
            tx_hash = chain.pool_event.objects.get(
                order_index=auction_auction_nft_settle.order_index
            )
            auction_auction_nft_settle.transaction_hash = tx_hash.transaction_hash
            auction_auction_nft_settle.save()

    def handle(self, *args, **options):
        chain = Ethereum()
        self.populate_tx_hash(chain)
