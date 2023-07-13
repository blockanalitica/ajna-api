from decimal import Decimal

from django.core.management.base import BaseCommand

from ajna.v1.ethereum.chain import EthereumModels


class Command(BaseCommand):
    def handle(self, *args, **options):
        models = EthereumModels()
        snapshots = models.pool_snapshot.objects.all()
        for snapshot in snapshots:
            if snapshot.debt > 0 and snapshot.pool_size > 0:
                snapshot.actual_utilization = snapshot.debt / snapshot.pool_size
            else:
                snapshot.actual_utilization = Decimal("0")
            snapshot.save()
