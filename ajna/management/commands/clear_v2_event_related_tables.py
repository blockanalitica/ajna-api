from django.core.management.base import BaseCommand

from ajna.v2.ethereum.chain import Ethereum
from ajna.v2.goerli.chain import Goerli


class Command(BaseCommand):
    def _clear_models(self, chain):
        chain.pool_event.objects.all().delete()

        chain.wallet_bucket_state.objects.all().delete()
        chain.bucket_state.objects.all().delete()
        chain.bucket.objects.all().delete()

        chain.wallet_position.objects.all().delete()
        chain.current_wallet_position.objects.all().delete()
        chain.walet.objects.all().delete()

    def handle(self, *args, **options):
        goerli = Goerli()
        self._clear_models(goerli)

        ethereum = Ethereum()
        self._clear_models(ethereum)
