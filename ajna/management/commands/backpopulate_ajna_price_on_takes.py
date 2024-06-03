from django.core.management.base import BaseCommand

from ajna.v4.arbitrum.chain import Arbitrum
from ajna.v4.base.chain import Base
from ajna.v4.blast.chain import Blast
from ajna.v4.ethereum.chain import Ethereum
from ajna.v4.gnosis.chain import Gnosis
from ajna.v4.mode.chain import Mode
from ajna.v4.modules.reserve_auctions import _get_ajna_price
from ajna.v4.optimism.chain import Optimism
from ajna.v4.polygon.chain import Polygon


class Command(BaseCommand):
    def handle(self, *args, **options):
        chains = [
            Ethereum(),
            Arbitrum(),
            Base(),
            Optimism(),
            Polygon(),
            Gnosis(),
            Blast(),
            Mode(),
        ]
        for chain in chains:
            self.stdout.write("Processing takes for chain {}".format(chain.chain))
            takes = chain.reserve_auction_take.objects.all()
            for take in takes:
                price = _get_ajna_price(chain, take.block_datetime)
                if price is None:
                    continue

                take.ajna_price = price
                take.save(update_fields=["ajna_price"])
