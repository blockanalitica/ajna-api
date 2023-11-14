from django.core.management.base import BaseCommand

from ajna.v2.ethereum.chain import Ethereum
from ajna.v2.goerli.chain import Goerli


class Command(BaseCommand):
    def populate_pool_token_symbol(self, chain):
        for pool in chain.pool.objects.all():
            c_token = chain.token.objects.get(
                underlying_address=pool.collateral_token_address
            )
            q_token = chain.token.objects.get(
                underlying_address=pool.quote_token_address
            )
            pool.collateral_token_symbol = c_token.symbol
            pool.quote_token_symbol = q_token.symbol
            pool.save()

    def handle(self, *args, **options):
        chain = Goerli()
        self.populate_pool_token_symbol(chain)
        chain = Ethereum()
        self.populate_pool_token_symbol(chain)
