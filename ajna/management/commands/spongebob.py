from collections import defaultdict
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import connection

from ajna.utils.db import fetch_all
from ajna.v1.ethereum.chain import Ethereum, EthereumModels
from ajna.v1.modules.positions import _handle_debt_events


class Command(BaseCommand):
    def handle(self, *args, **options):
        chain = Ethereum()

        curr_positions = defaultdict(lambda: defaultdict(Decimal))

        models = EthereumModels()
        wallet_address = "0xade0f7c5070b051bc78838f02ad3114027dd40f4"
        _handle_debt_events(chain, wallet_address, 0, curr_positions)

        print(curr_positions)
        # save_wallet_positions(models, wallet_address)

        # debt_sql = """

        #         SELECT
        #             *
        #         FROM {draw_debt_table} AS dd
        #         WHERE dd.borrower = %s

        # """.format(
        #     draw_debt_table=models.draw_debt._meta.db_table,
        #     # repay_debt_table=models.repay_debt._meta.db_table,
        # )

        # with connection.cursor() as cursor:
        #     cursor.execute(debt_sql, [wallet_address])
        #     events = fetch_all(cursor)

        # print(events)

        # _get_inflator
