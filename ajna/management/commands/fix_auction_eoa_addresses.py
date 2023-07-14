from django.core.management.base import BaseCommand

from ajna.v1.ethereum.chain import Ethereum, EthereumModels
from ajna.v1.goerli.chain import Goerli, GoerliModels
from ajna.v1.modules.auctions import _get_wallet_address


class Command(BaseCommand):
    def _fix_eth(self):
        self.stdout.write("Fixing ethereum auctions")
        chain = Ethereum()
        models = EthereumModels()
        auctions = models.liqudation_auction.objects.all()
        for auction in auctions:
            auction.wallet_address = _get_wallet_address(chain, auction.borrower)
            auction.save()

    def _fix_goerli(self):
        self.stdout.write("Fixing goerli auctions")
        chain = Goerli()
        models = GoerliModels()
        auctions = models.liqudation_auction.objects.all()
        for auction in auctions:
            auction.wallet_address = _get_wallet_address(chain, auction.borrower)
            auction.save()

    def handle(self, *args, **options):
        self._fix_eth()
        self._fix_goerli()
