from django.core.management.base import BaseCommand

from ajna.v2.ethereum.chain import Ethereum


class Command(BaseCommand):
    def handle(self, *args, **options):
        chain = Ethereum()

        pools = chain.pool.objects.all()

        for pool in pools:
            event = (
                chain.pool_event.objects.filter(pool_address=pool.address)
                .order_by("-order_index")
                .first()
            )

            if event:
                pool.last_block_number = event.block_number
                pool.save()
