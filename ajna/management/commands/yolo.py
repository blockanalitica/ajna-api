from django.core.management.base import BaseCommand

from ajna.v1.ethereum.chain import Ethereum as V1Ethereum
from ajna.v1.goerli.chain import Goerli as V1Goerli
from ajna.v3.ethereum import tasks

# from ajna.v3.goerli import tasks


class Command(BaseCommand):
    def handle(self, *args, **options):
        tasks.fetch_erc721_pool_created_events_task()
        tasks.fetch_erc20_pools_data_task()
        tasks.fetch_erc721_pools_data_task()
        tasks.fetch_and_save_events_for_all_pools_task()
        tasks.fetch_erc20_pool_created_events_task()
        tasks.process_events_for_all_pools_task()
