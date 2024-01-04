from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.db import connection

from ajna.v3.goerli.chain import MODEL_MAP, Goerli


class Command(BaseCommand):
    def handle(self, *args, **options):
        chain = Goerli()

        cache_key = "fetch_and_save_events_for_all_pools.{}.last_block_number".format(
            chain.unique_key
        )
        cache.delete(cache_key)

        cache_key = "fetch_and_save_grant_proposals.{}.last_block_number".format(
            chain.unique_key
        )
        cache.delete(cache_key)

        for key, model in MODEL_MAP.items():
            if key == "price_feed":
                self.stdout.write("Skipping price_feed model: {}".format(model))
                continue

            self.stdout.write("Truncating model: {}".format(model))
            with connection.cursor() as cursor:
                cursor.execute("TRUNCATE TABLE {}".format(model._meta.db_table))