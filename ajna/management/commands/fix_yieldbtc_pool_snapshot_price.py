from django.core.management.base import BaseCommand

from ajna.v1.ethereum.chain import EthereumModels


class Command(BaseCommand):
    def handle(self, *args, **options):
        models = EthereumModels()
        snapshots = models.pool_snapshot.objects.filter(
            address="0x67a64e974bfeaded23cf479e27654d8face82126",
            collateral_token_price__isnull=True,
        )
        cnt = snapshots.count()
        self.stdout.write("Updating {} snapshots".format(cnt))
        if cnt:
            pf = models.price_feed.objects.filter(
                underlying_address="0x0274a704a6d9129f90a62ddc6f6024b33ecdad36"
            ).first()
            snapshots.update(collateral_token_price=pf.price)
