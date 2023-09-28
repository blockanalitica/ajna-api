from django.core.management.base import BaseCommand

from ajna.v2.ethereum.chain import Ethereum
from ajna.v2.goerli.chain import Goerli
from ajna.v2.modules.positions import EventProcessor
from ajna.v2.modules.events import (
    _get_bucket_indexes,
    _get_wallet_addresses,
    fetch_and_save_events_for_all_pools,
)
from web3 import Web3


class Command(BaseCommand):
    def handle(self, *args, **options):
        # chain = Goerli()
        chain = Ethereum()

        # chain.wallet_bucket_state.objects.all().delete()
        # chain.bucket_state.objects.all().delete()
        # chain.bucket.objects.all().delete()
        # chain.wallet_position.objects.all().delete()
        # chain.current_wallet_position.objects.all().delete()
        # chain.wallet.objects.all().delete()

        # processor = EventProcessor(chain)
        # processor.process_all_events()

        # chain.pool_event.objects.all().delete()

        # fetch_and_save_events_for_all_pools(chain)
        # from_block = chain.erc20_pool_factory_start_block
        # to_block = chain.get_latest_block()

        # pool_addresses = list(
        #     chain.pool.objects.all().values_list("address", flat=True)
        # )

        # pool_addresses = [
        #     Web3.to_checksum_address(address) for address in pool_addresses
        # ]
        # events = chain.get_events_for_contracts(
        #     pool_addresses, from_block=from_block, to_block=to_block
        # )

        # for event in events:
        #     # _get_bucket_indexes(event)
        #     _get_wallet_addresses(event)

        bla = chain.wallet_position.objects.filter(
            wallet_address="0xef764bac8a438e7e498c2e5fccf0f174c3e3f8db",
            block_number__lt=18175585
        )

        print(len(bla))
        for x in bla:
            print(x.__dict__)
