from django.core.management.base import BaseCommand

from ajna.utils.wad import wad_to_decimal
from ajna.v2.ethereum.chain import Ethereum
from ajna.v2.goerli.chain import Goerli


class Command(BaseCommand):
    def _do_work(self, chain):
        blocks = set(
            chain.current_wallet_position.objects.filter(t0debt__gt=0)
            .values_list("block_number", flat=True)
            .distinct()
        )
        self.stdout.write("Blocks to update {}".format(len(blocks)))
        calls = []
        for index, block in enumerate(blocks):
            self.stdout.write("Updating block {} index {}".format(block, index))
            curr_positions = chain.current_wallet_position.objects.filter(
                block_number=block
            )
            for position in curr_positions:
                calls.append(
                    (
                        position.pool_address,
                        [
                            "borrowerInfo(address)((uint256,uint256,uint256))",
                            position.wallet_address,
                        ],
                        [f"{position.pool_address}:{position.wallet_address}", None],
                    )
                )

            results = chain.multicall(calls, block_identifier=block)
            for position in curr_positions:
                data = results[f"{position.pool_address}:{position.wallet_address}"]
                position.t0np = wad_to_decimal(data[2])
                position.save(update_fields=["t0np"])

    def handle(self, *args, **options):
        goerli = Goerli()
        self._do_work(goerli)

        ethereum = Ethereum()
        self._do_work(ethereum)
