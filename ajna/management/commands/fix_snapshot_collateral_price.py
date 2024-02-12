from datetime import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand

from ajna.v4.ethereum.chain import Ethereum


class Command(BaseCommand):
    def handle(self, *args, **options):
        pool_address = "0x64aa997236996823a53b8b30ead599aa2f0382fa"

        chain = Ethereum()
        chain.pool_snapshot.objects.filter(
            address=pool_address,
            datetime__gte=datetime(2024, 2, 10),
        ).update(collateral_token_price=Decimal("0.948816403825876615"))

        chain.celery_tasks.save_network_stats_for_yesterday_task.delay()
