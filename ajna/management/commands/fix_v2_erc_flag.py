from django.core.management.base import BaseCommand

from ajna.constants import ERC20, ERC721
from ajna.v2.ethereum.chain import Ethereum
from ajna.v2.goerli.chain import Goerli


class Command(BaseCommand):
    def _do_work(self, chain, pool_factory_address, from_block_number, erc):
        events = chain.get_events_for_contract_topics(
            pool_factory_address,
            ["0x83a48fbcfc991335314e74d0496aab6a1987e992ddc85dddbcc4d6dd6ef2e9fc"],
            from_block_number,
        )

        for event in events:
            pool_address = event["args"]["pool_"].lower()
            try:
                pool = chain.pool.objects.get(address=pool_address)
            except chain.pool.DoesNotExist:
                pass
            else:
                pool.erc = erc
                pool.save(update_fields=["erc"])

    def _just_do_it(self, chain):
        self._do_work(
            chain,
            chain.erc20_pool_factory_address,
            chain.erc20_pool_factory_start_block,
            ERC20,
        )
        self._do_work(
            chain,
            chain.erc721_pool_factory_address,
            chain.erc721_pool_factory_start_block,
            ERC721,
        )

    def handle(self, *args, **options):
        goerli = Goerli()
        self._just_do_it(goerli)

        ethereum = Ethereum()
        self._just_do_it(ethereum)
