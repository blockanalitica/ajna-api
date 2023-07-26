from datetime import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand

from ajna.sources.subgraph import EthereumSubgraph, GoerliSubgraph
from ajna.utils.graphql import GraphqlClient
from ajna.utils.utils import datetime_to_next_full_hour
from ajna.v1.ethereum.chain import EthereumModels
from ajna.v1.goerli.chain import GoerliModels


class BlockSubgraph:
    def _fetch_all_by_field(self, query, key, field, value, page_size=1000):
        while True:
            variables = {
                field: value,
                "first": page_size,
            }

            results = self.client.execute(query, variables=variables)

            if "data" not in results:
                return None

            data = results["data"][key]

            # Don't use `yield from data` to take advantage of orphaned last row
            for row in data:  # noqa: SIM104
                yield row

            if len(data) < page_size:
                break

            # Since we're looping through all data above, we can harness the pythons
            # way of exposing last row from the loop
            value = int(row[field])


class EthBlockSubgraph(BlockSubgraph):
    def __init__(self, *args, **kwargs):
        self.client = GraphqlClient(
            endpoint="https://api.thegraph.com/subgraphs/name/stakewise/ethereum-mainnet"
        )


class GoerliBlockSubgraph(BlockSubgraph):
    def __init__(self, *args, **kwargs):
        self.client = GraphqlClient(
            endpoint="https://api.thegraph.com/subgraphs/name/dramacrypto/goerli-blocks"
        )


class Command(BaseCommand):
    def _fix_goerli(self):
        goerli_blocks = self._get_goerli_blocks()
        models = GoerliModels()

        self.stdout.write("Fixing goerli pool snapshot lend_rate")
        subgraph = GoerliSubgraph()

        for dt, block in goerli_blocks.items():
            query = """
                query ($block: Int) {
                  pools(block: {number: $block}) {
                    id
                    lendRate
                  }
                }
            """
            results = subgraph.client.execute(query, variables={"block": int(block)})
            pools = results["data"]["pools"]

            for pool in pools:
                try:
                    snapshot = models.pool_snapshot.objects.get(
                        address=pool["id"], datetime=dt
                    )
                except models.pool_snapshot.DoesNotExist:
                    self.stdout.write("ERROR {} {} {}".format(block, dt, pool))
                    continue

                if snapshot.lend_rate != Decimal(pool["lendRate"]):
                    snapshot.lend_rate = Decimal(pool["lendRate"])
                    snapshot.save(update_fields=["lend_rate"])

    def _fix_ethereum(self):
        eth_blocks = self._get_eth_blocks()
        models = EthereumModels()

        print(eth_blocks)

        self.stdout.write("Fixing ethereum pool snapshot lend_rate")
        subgraph = EthereumSubgraph()

        for dt, block in eth_blocks.items():
            query = """
                query ($block: Int) {
                  pools(block: {number: $block}) {
                    id
                    lendRate
                  }
                }
            """
            results = subgraph.client.execute(query, variables={"block": int(block)})
            pools = results["data"]["pools"]

            for pool in pools:
                try:
                    snapshot = models.pool_snapshot.objects.get(
                        address=pool["id"], datetime=dt
                    )
                except models.pool_snapshot.DoesNotExist:
                    self.stdout.write("ERROR {} {} {}".format(block, dt, pool))
                    continue

                if snapshot.lend_rate != Decimal(pool["lendRate"]):
                    snapshot.lend_rate = Decimal(pool["lendRate"])
                    snapshot.save(update_fields=["lend_rate"])

    def _get_eth_blocks(self):
        self.stdout.write("Fetching eth blocks")

        block_number = 17667177

        query = """
            query (
                $first: Int, $id: Int
            ) {
              blocks(
                first: $first
                orderBy: id
                orderDirection: asc
                where: {id_gt: $id}
              ) {
                id
                timestamp
              }
            }
        """
        block_map = {}
        client = EthBlockSubgraph()
        blocks = client._fetch_all_by_field(
            query, "blocks", "id", block_number, page_size=1000
        )
        for block in blocks:
            dt = datetime_to_next_full_hour(
                datetime.fromtimestamp(int(block["timestamp"]))
            )
            block_map[dt] = block["id"]

        return block_map

    def _get_goerli_blocks(self):
        self.stdout.write("Fetching goerli blocks")

        block_number = 9293748

        query = """
            query (
                $first: Int, $number: Int
            ) {
              blocks(
                first: $first
                orderBy: number
                orderDirection: asc
                where: {number_gt: $number}
              ) {
                number
                timestamp
              }
            }
        """
        block_map = {}
        client = GoerliBlockSubgraph()

        blocks = client._fetch_all_by_field(
            query, "blocks", "number", block_number, page_size=1000
        )
        for block in blocks:
            dt = datetime_to_next_full_hour(
                datetime.fromtimestamp(int(block["timestamp"]))
            )
            block_map[dt] = block["number"]

        return block_map

    def handle(self, *args, **options):
        self._fix_goerli()
        self._fix_ethereum()
