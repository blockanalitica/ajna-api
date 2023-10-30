from django.core.management.base import BaseCommand

from ajna.v1.ethereum.chain import Ethereum as V1Ethereum
from ajna.v1.goerli.chain import Goerli as V1Goerli
from ajna.v2.ethereum.chain import Ethereum
from ajna.v2.goerli.chain import Goerli


class Command(BaseCommand):
    def _do_work(self, v1, v2):
        pools = v2.pool.objects.all()

        for pool in pools:
            first_snapshot = (
                v2.pool_snapshot.objects.filter(address=pool.address)
                .order_by("datetime")
                .first()
            )

            filters = {}
            if first_snapshot:
                filters["datetime__lt"] = first_snapshot.datetime

            snapshots = v1.pool_snapshot.objects.filter(
                address=pool.address, **filters
            ).values()

            snaps = []
            for snapshot in snapshots:
                del snapshot["id"]
                snaps.append(v2.pool_snapshot(**snapshot))

                if len(snaps) > 100:
                    v2.pool_snapshot.objects.bulk_create(snaps)
                    snaps = []

            if len(snaps) > 100:
                v2.pool_snapshot.objects.bulk_create(snaps)

    def handle(self, *args, **options):
        v1_goerli = V1Goerli()
        v2_goerli = Goerli()
        self._do_work(v1_goerli, v2_goerli)

        v1_ethereum = V1Ethereum()
        v2_ethereum = Ethereum()
        self._do_work(v1_ethereum, v2_ethereum)
