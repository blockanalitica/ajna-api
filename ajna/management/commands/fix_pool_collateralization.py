from django.core.management.base import BaseCommand

from ajna.v1.ethereum.chain import EthereumModels


class Command(BaseCommand):
    def handle(self, *args, **options):
        models = EthereumModels()

        snapshots = models.pool_snapshot.objects.all()

        for snapshot in snapshots:
            collateralization = None
            if (
                snapshot.t0debt > 0
                and snapshot.pending_inflator > 0
                and snapshot.quote_token_price
                and snapshot.collateral_token_price
            ):
                collateralization = (
                    snapshot.pledged_collateral * snapshot.collateral_token_price
                ) / (
                    snapshot.t0debt
                    * snapshot.pending_inflator
                    * snapshot.quote_token_price
                )

            snapshot.collateralization = collateralization
            snapshot.save()
