from datetime import datetime

from django.core.management.base import BaseCommand

from ajna.v1.ethereum.models import V1EthereumPriceFeed
from ajna.v1.goerli.models import V1GoerliPriceFeed
from ajna.v2.ethereum.models import V2EthereumPriceFeed
from ajna.v2.goerli.models import V2GoerliPriceFeed


class Command(BaseCommand):
    def _populate_eth(self):
        pfs = V1EthereumPriceFeed.objects.all().order_by("timestamp")
        to_create = []
        for pf in pfs.iterator():
            to_create.append(
                V2EthereumPriceFeed(
                    price=pf.price,
                    timestamp=pf.timestamp,
                    datetime=pf.datetime,
                    underlying_address=pf.underlying_address,
                )
            )
            if len(to_create) > 500:
                V2EthereumPriceFeed.objects.bulk_create(
                    to_create, ignore_conflicts=True
                )
                to_create = []

        if to_create:
            V2EthereumPriceFeed.objects.bulk_create(to_create, ignore_conflicts=True)

    def _populate_goerli(self):
        pfs = V1GoerliPriceFeed.objects.all().order_by("timestamp")
        to_create = []
        for pf in pfs.iterator():
            to_create.append(
                V2GoerliPriceFeed(
                    price=pf.price,
                    timestamp=pf.timestamp,
                    datetime=pf.datetime,
                    underlying_address=pf.underlying_address,
                )
            )
            if len(to_create) > 500:
                V2GoerliPriceFeed.objects.bulk_create(to_create, ignore_conflicts=True)
                to_create = []

        if to_create:
            V2GoerliPriceFeed.objects.bulk_create(to_create, ignore_conflicts=True)

    def handle(self, *args, **options):
        start = datetime.now()
        self.stdout.write("Populating mainnet")
        self._populate_eth()
        self.stdout.write("Finished mainnet in {}".format(datetime.now() - start))
        start = datetime.now()
        self.stdout.write("Populating goerli")
        self._populate_goerli()
        self.stdout.write("Finished goerli in {}".format(datetime.now() - start))
