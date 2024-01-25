om decimal import Decimal

from django.core.management.base import BaseCommand

from ajna.utils.db import fetch_one
from ajna.v2.ethereum.chain import Ethereum as V2Ethereum
from ajna.v3.arbitrum.chain import Arbitrum as V3Arbitrum
from ajna.v3.base.chain import Base as V3Base
from ajna.v3.optimism.chain import Optimism as V3Optimism
from ajna.v3.polygon.chain import Polygon as V3Polygon
from ajna.v4.arbitrum.chain import Arbitrum
from ajna.v4.base.chain import Base
from ajna.v4.ethereum.chain import Ethereum
from ajna.v4.goerli.chain import Goerli
from ajna.v4.optimism.chain import Optimism
from ajna.v4.polygon.chain import Polygon


class Command(BaseCommand):
    def _calculate_supply(self, chain, position):
        sql = """
            SELECT
                SUM(x.deposit) AS supply
            FROM (
                SELECT DISTINCT ON (bucket_index)
                    deposit
                FROM
                    {wallet_bucket_state_table}
                WHERE
                    pool_address = %s AND wallet_address = %s AND block_number <= %s
                ORDER BY
                    bucket_index, block_number DESC
            ) x
        """.format(
            wallet_bucket_state_table=chain.wallet_bucket_state._meta.db_table
        )

        data = fetch_one(
            sql,
            [position.pool_address, position.wallet_address, position.block_number],
        )
        return data["supply"] or Decimal("0")

    def _do_work(self, chain, positions):
        for position in positions:
            supply = self._calculate_supply(chain, position)
            if supply != position.supply:
                self.stdout.write(position.supply, supply)
                position.supply = supply
                position.save(update_fields=["supply"])

    def _fix_chain(self, chain):
        positions = chain.current_wallet_position.objects.all()
        self._do_work(chain, positions)

        positions = chain.wallet_position.objects.all()
        self._do_work(chain, positions)

    def _handle_v4(self):
        self.stdout.write("Fixing mainnet")
        eth = Ethereum()
        self._fix_chain(eth)

        self.stdout.write("Fixing goerli")
        go = Goerli()
        self._fix_chain(go)

        self.stdout.write("Fixing arbitrum")
        arb = Arbitrum()
        self._fix_chain(arb)

        self.stdout.write("Fixing base")
        base = Base()
        self._fix_chain(base)

        self.stdout.write("Fixing polygon")
        poly = Polygon()
        self._fix_chain(poly)

        self.stdout.write("Fixing optimism")
        op = Optimism()
        self._fix_chain(op)

    def _handle_v3(self):
        self.stdout.write("Fixing arbitrum")
        arb = V3Arbitrum()
        self._fix_chain(arb)

        self.stdout.write("Fixing base")
        base = V3Base()
        self._fix_chain(base)

        self.stdout.write("Fixing polygon")
        poly = V3Polygon()
        self._fix_chain(poly)

        self.stdout.write("Fixing optimism")
        op = V3Optimism()
        self._fix_chain(op)

    def _handle_v2(self):
        self.stdout.write("Fixing ethereum")
        eth = V2Ethereum()
        self._fix_chain(eth)

    def handle(self, *args, **options):
        self.stdout.write("V4")
        self._handle_v4()
        self.stdout.write("V3")
        self._handle_v3()
        self.stdout.write("V2")
        self._handle_v2()