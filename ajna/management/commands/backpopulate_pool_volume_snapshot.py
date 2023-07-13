from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from ajna.v1.goerli.chain import GoerliModels
from ajna.v1.modules.pools import calculate_pool_volume_for_date


class Command(BaseCommand):
    def handle(self, *args, **options):
        days = 30
        self.stdout.write("Backpopulating for {} days back.".format(days))
        models = GoerliModels()
        for days_ago in range(days):
            date = datetime.now() - timedelta(days=days_ago)
            self.stdout.write("Backpopulating for date {}".format(date.date()))

            calculate_pool_volume_for_date(models, date)
