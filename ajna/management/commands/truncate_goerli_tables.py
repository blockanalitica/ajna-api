from django.core.management.base import BaseCommand
from django.db import connection

from ajna.v1.goerli.chain import MODEL_MAP


class Command(BaseCommand):
    def handle(self, *args, **options):
        for key, model in MODEL_MAP.items():
            if key == "price_feed":
                self.stdout.write("Skipping price_feed model: {}".format(model))
                continue

            self.stdout.write("Truncating model: {}".format(model))
            with connection.cursor() as cursor:
                cursor.execute("TRUNCATE TABLE {}".format(model._meta.db_table))
