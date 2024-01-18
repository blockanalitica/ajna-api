from datetime import date

from django.core.management.base import BaseCommand

from ajna.v3.models import V3NetworkStatsDaily
from ajna.v4.models import V4NetworkStatsDaily


class Command(BaseCommand):
    def handle(self, *args, **options):
        old_stats = V3NetworkStatsDaily.objects.filter(
            network="ethereum", date__lt=date.today()
        )
        for stat in old_stats:
            V4NetworkStatsDaily.objects.create(
                network=stat.network,
                date=stat.date,
                tvl=stat.tvl,
                collateral_usd=stat.collateral_usd,
                supply_usd=stat.supply_usd,
                debt_usd=stat.debt_usd,
            )
