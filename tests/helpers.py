import random
from decimal import Decimal

BORROWER = "0x5c9d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d"


def generate_ethereum_address():
    return "0x{}".format("".join(random.choices("0123456789abcdef", k=40)))


def generate_transaction_hash():
    return "0x{}".format("".join(random.choices("0123456789abcdef", k=40)))


def create_active_auction(
    models, pool_address, uid, kick_time, collateral_remaining=10, debt_remaining=100
):
    auction = models["auction"].objects.create(
        uid=uid,
        pool_address=pool_address,
        borrower=BORROWER,
        collateral=Decimal(10),
        collateral_remaining=Decimal(collateral_remaining),
        debt=Decimal(100),
        debt_remaining=Decimal(debt_remaining),
    )
    models["auction_kick"].objects.create(
        order_index=uid,
        auction_uid=auction.uid,
        pool_address=pool_address,
        borrower=BORROWER,
        kicker=BORROWER,
        debt=Decimal(100),
        collateral=Decimal(10),
        bond=Decimal(1),
        locked=Decimal(0),
        starting_price=Decimal(1),
        block_number=int(kick_time.timestamp()),
        block_datetime=kick_time,
    )
    return auction


def get_result_uids(client, url, params):
    response = client.get(url, params)

    assert response.status_code == 200
    return [row["uid"] for row in response.json()["results"]]
