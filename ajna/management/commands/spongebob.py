from django.core.management.base import BaseCommand
from django.db import connection

from ajna.v1.modules.positions import *
from ajna.v1.ethereum.chain import Ethereum, EthereumModels

from django.db import connection

from ajna.utils.db import fetch_all


class Command(BaseCommand):
    def handle(self, *args, **options):
        # chain = Ethereum()
        models = EthereumModels()
        wallet_address = "0xade0f7c5070b051bc78838f02ad3114027dd40f4"
        # save_wallet_positions(models, wallet_address)

        debt_sql = """
        
                SELECT
                    *
                FROM {draw_debt_table} AS dd
                WHERE dd.borrower = %s

        """.format(
            draw_debt_table=models.draw_debt._meta.db_table,
            # repay_debt_table=models.repay_debt._meta.db_table,
        )

        with connection.cursor() as cursor:
            cursor.execute(debt_sql, [wallet_address])
            events = fetch_all(cursor)

        print(events)


[
    {
        "id": 187,
        "pool_address": "0x8519be08b8d83baeb11eba52a7889967dced9ae0",
        "borrower": "0xade0f7c5070b051bc78838f02ad3114027dd40f4",
        "amount_borrowed": Decimal("150000.000000000000000000"),
        "collateral_pledged": Decimal("190.000000000000000000"),
        "lup": Decimal("1453.617572727602393951"),
        "block_number": 17732992,
        "block_timestamp": 1689839339,
        "transaction_hash": "0xf40d6e70eaf5da6029fc85d0a87dc1766f2be428a5fb89dff2a1312f17754de0",
        "index": "0xf40d6e70eaf5da6029fc85d0a87dc1766f2be428a5fb89dff2a1312f17754de028000000",
        "collateral_token_price": Decimal("2164.410000000000000000"),
        "fee": Decimal("75.000000000000000000"),
        "quote_token_price": Decimal("1.000000000000000000"),
        "borrow_fee_rate": Decimal("0.000500000000000000"),
    },
    {
        "id": 190,
        "pool_address": "0x8519be08b8d83baeb11eba52a7889967dced9ae0",
        "borrower": "0xade0f7c5070b051bc78838f02ad3114027dd40f4",
        "amount_borrowed": Decimal("116583.935064947856018980"),
        "collateral_pledged": Decimal("150.000000000000000000"),
        "lup": Decimal("1453.617572727602393951"),
        "block_number": 17733076,
        "block_timestamp": 1689840347,
        "transaction_hash": "0x3845b3452cb5c703805c4b2452bdc799ab30219cb7c05d6102e082ea7c17b00f",
        "index": "0x3845b3452cb5c703805c4b2452bdc799ab30219cb7c05d6102e082ea7c17b00f77000000",
        "collateral_token_price": Decimal("2164.820000000000000000"),
        "fee": Decimal("58.291967532473928009"),
        "quote_token_price": Decimal("0.999592000000000000"),
        "borrow_fee_rate": Decimal("0.000500000000000000"),
    },
    {
        "id": 200,
        "pool_address": "0x8519be08b8d83baeb11eba52a7889967dced9ae0",
        "borrower": "0xade0f7c5070b051bc78838f02ad3114027dd40f4",
        "amount_borrowed": Decimal("60000.000000000000000000"),
        "collateral_pledged": Decimal("80.000000000000000000"),
        "lup": Decimal("1453.617572727602393951"),
        "block_number": 17734813,
        "block_timestamp": 1689861383,
        "transaction_hash": "0x26e0db378206e4da4f2978412ff9f2e08b38b5aca97dc2925b3cfc3751e76064",
        "index": "0x26e0db378206e4da4f2978412ff9f2e08b38b5aca97dc2925b3cfc3751e7606420000000",
        "collateral_token_price": Decimal("2172.480000000000000000"),
        "fee": Decimal("30.000000000000000000"),
        "quote_token_price": Decimal("0.999834000000000000"),
        "borrow_fee_rate": Decimal("0.000500000000000000"),
    },
    {
        "id": 234,
        "pool_address": "0x8519be08b8d83baeb11eba52a7889967dced9ae0",
        "borrower": "0xade0f7c5070b051bc78838f02ad3114027dd40f4",
        "amount_borrowed": Decimal("363754.741038633176312702"),
        "collateral_pledged": Decimal("400.000000000000000000"),
        "lup": Decimal("1453.617572727602393951"),
        "block_number": 17750069,
        "block_timestamp": 1690045823,
        "transaction_hash": "0x89b9933e1b716a94ad1caaa6ceb2efa34385ccd069999ba589ec8e1fd78b766c",
        "index": "0x89b9933e1b716a94ad1caaa6ceb2efa34385ccd069999ba589ec8e1fd78b766cec000000",
        "collateral_token_price": Decimal("2140.130000000000000000"),
        "fee": Decimal("181.877370519316588156"),
        "quote_token_price": Decimal("0.999342000000000000"),
        "borrow_fee_rate": Decimal("0.000500000000000000"),
    },
]
