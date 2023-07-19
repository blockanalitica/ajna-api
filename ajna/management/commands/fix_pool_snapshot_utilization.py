from decimal import Decimal
from django.core.management.base import BaseCommand

from ajna.v1.goerli.chain import GoerliModels
from ajna.v1.ethereum.chain import EthereumModels


class Command(BaseCommand):
    def _fix_goerli(self):
        models = GoerliModels()
        snapshots = models.pool_snapshot.objects.filter(utilization__isnull=True)
        self.stdout.write(
            "Fixing {} goerli pool snapshot utilization".format(snapshots.count())
        )
        for snapshot in snapshots:
            utilization = Decimal("0")
            if snapshot.pool_size > 0:
                utilization = snapshot.debt / snapshot.pool_size

            snapshot.utilization = utilization
            snapshot.save(update_fields=["utilization"])

    def _fix_ethereum(self):
        models = EthereumModels()
        snapshots = models.pool_snapshot.objects.filter(utilization__isnull=True)
        self.stdout.write(
            "Fixing {} ethereum pool snapshot utilization".format(snapshots.count())
        )
        for snapshot in snapshots:
            utilization = Decimal("0")
            if snapshot.pool_size > 0:
                utilization = snapshot.debt / snapshot.pool_size

            snapshot.utilization = utilization
            snapshot.save(update_fields=["utilization"])

    def handle(self, *args, **options):
        self._fix_goerli()
        self._fix_ethereum()
