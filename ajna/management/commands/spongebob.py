from datetime import datetime
from collections import defaultdict
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import connection

from ajna.utils.db import fetch_all
from ajna.utils.wad import wad_to_decimal

# from ajna.v1.ethereum.chain import Ethereum, EthereumModels
from ajna.v1.goerli.chain import Goerli
from ajna.v1.modules.positions import _handle_debt_events, save_wallet_positions


def _get_addresses_from_events(chain):
    sql = """
        SELECT DISTINCT
              x.wallet_address
        FROM (
            SELECT DISTINCT
                 dd.borrower AS wallet_address
            FROM {draw_debt_table} AS dd
            WHERE dd.block_number >= %s

            UNION

            SELECT DISTINCT
                rd.borrower AS wallet_address
            FROM {repay_debt_table} rd
            WHERE rd.block_number >= %s

            UNION

            SELECT DISTINCT
                aqt.lender AS wallet_address
            FROM {add_quote_token_table} AS aqt
            WHERE aqt.block_number >= %s

            UNION

            SELECT DISTINCT
                rqt.lender AS wallet_address
            FROM {remove_quote_token_table} rqt
            WHERE rqt.block_number >= %s

            UNION

            SELECT DISTINCT
                mqt.lender AS wallet_address
            FROM {move_quote_token_table} mqt
            WHERE mqt.block_number >= %s

            UNION

            SELECT
                ac.actor AS wallet_address
            FROM {add_collateral_table} AS ac
            WHERE ac.block_number >= %s

            UNION

            SELECT
                rc.claimer AS wallet_address
            FROM {remove_collateral_table} rc
            WHERE rc.block_number >= %s
        ) x
    """.format(
        draw_debt_table=chain.draw_debt._meta.db_table,
        repay_debt_table=chain.repay_debt._meta.db_table,
        add_quote_token_table=chain.add_quote_token._meta.db_table,
        remove_quote_token_table=chain.remove_quote_token._meta.db_table,
        move_quote_token_table=chain.move_quote_token._meta.db_table,
        add_collateral_table=chain.add_collateral._meta.db_table,
        remove_collateral_table=chain.remove_collateral._meta.db_table,
    )
    with connection.cursor() as cursor:
        cursor.execute(sql, [0] * 7)
        addresses = fetch_all(cursor)

    return set(a["wallet_address"] for a in addresses)


# 394.743070866156254789


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Wrong t0debt and debt 0x550c35d76789c65a41ff0a675146ddb5a4231356
        # 0x67dc5526dee74483965ae5959ab0a3c549f91fbc
        chain = Goerli()

        # calls = [
        #     (
        #         "0xcdf3047503923b1e1fdf2190aafe3254a7f1a632",
        #         [
        #             "borrowerInfo(address)((uint256,uint256,uint256))",
        #             "0x550c35d76789c65a41ff0a675146ddb5a4231356",
        #         ],
        #         ["omg", None],
        #     ),
        #     (
        #         "0xcdf3047503923b1e1fdf2190aafe3254a7f1a632",
        #         ["interestRateInfo()((uint256,uint256))"],
        #         ["wtf", None],
        #     ),

        #                 (
        #         "0xcdf3047503923b1e1fdf2190aafe3254a7f1a632",
        #         ["inflatorInfo()((uint256,uint256))"],
        #         ["aaa", None],
        #     ),
        # ]

        # data = chain.call_multicall(calls, block_id=9321525)

        # omg = data["omg"]
        # print(
        #     {
        #         "t0debt": wad_to_decimal(omg[0]),
        #         "collateral": wad_to_decimal(omg[1]),
        #         "t0Np": wad_to_decimal(omg[2]),
        #         "borrow_rate": wad_to_decimal(data["wtf"][0]),
        #         "inflator": wad_to_decimal(data["aaa"][0]),
        #         "inflator_dt": datetime.fromtimestamp(data["aaa"][1]),
        #     }
        # )

        394.743070866156254789
        394.743070866156254789
        
        # 394.743070866156256849239446

        # 394.743070866156254002

        # curr_positions = defaultdict(lambda: defaultdict(Decimal))

        # wallet_addresses = _get_addresses_from_events(chain)
        # for wallet_address in wallet_addresses:
        # wallet_address = "0x67dc5526dee74483965ae5959ab0a3c549f91fbc"
        wallet_address = "0x550c35d76789c65a41ff0a675146ddb5a4231356"
        start = datetime.now()
        save_wallet_positions(chain, wallet_address, 0)
        print(wallet_address, datetime.now() - start)

        # {
        #     "id": 130,
        #     "wallet_address": "0x550c35d76789c65a41ff0a675146ddb5a4231356",
        #     "pool_address": "0xcdf3047503923b1e1fdf2190aafe3254a7f1a632",
        #     "supply": Decimal("0"),
        #     "collateral": Decimal("5.299999999999999999"),
        #     "t0debt": Decimal("393.704616953398910877"),
        #     "debt": Decimal("383.000000000000000000"),
        #     "datetime": datetime.datetime(2023, 8, 18, 1, 24, 12),
        #     "block_number": 9536435,
        # }

        # print(wallet_addresses)

        # wallet_address = "0x073db1fa5bbdaf38de96165e70160087fd85f51b"
        # save_wallet_positions(chain, wallet_address, 0)

        # _handle_debt_events(chain, wallet_address, 0, curr_positions)

        # print(curr_positions)
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
