from django.core.management.base import BaseCommand

from ajna.v2.ethereum.chain import Ethereum
from ajna.v2.goerli.chain import Goerli


class Command(BaseCommand):
    def _populate_eth(self, chain):
        wallets = chain.wallet.objects.filter(eoa__isnull=True)

        for wallet in wallets:
            wallet.eoa = chain.get_eoa(wallet.address)
            wallet.save()

    def handle(self, *args, **options):
        chain = Ethereum()
        self._populate_eth(chain)
        chain = Goerli()
        self._populate_eth(chain)
