from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from ajna.v4.base.models import V4BaseAuction, V4BaseAuctionKick, V4BasePool
from tests.factories import PoolFactory

URL = "/v4/base/auctions/active/"
BORROWER = "0x5c9d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d"
FIRST_KICK_TIME = datetime(2026, 1, 1, tzinfo=UTC)


class BasePoolFactory(PoolFactory):
    class Meta:
        model = V4BasePool


def _create_auction(pool, uid, debt_remaining, kicked_hours_after_start):
    auction = V4BaseAuction.objects.create(
        uid=uid,
        pool_address=pool.address,
        borrower=BORROWER,
        collateral=Decimal(10),
        collateral_remaining=Decimal(10),
        debt=Decimal(100),
        debt_remaining=Decimal(debt_remaining),
    )
    V4BaseAuctionKick.objects.create(
        order_index=uid,
        auction_uid=auction.uid,
        pool_address=pool.address,
        borrower=BORROWER,
        kicker=BORROWER,
        debt=Decimal(100),
        collateral=Decimal(10),
        bond=Decimal(1),
        locked=Decimal(0),
        starting_price=Decimal(1),
        block_number=kicked_hours_after_start + 1,
        block_datetime=FIRST_KICK_TIME + timedelta(hours=kicked_hours_after_start),
    )


@pytest.fixture
def auctions():
    pool = BasePoolFactory()
    _create_auction(pool, "auction-1", "300", kicked_hours_after_start=0)
    _create_auction(pool, "auction-2", "100", kicked_hours_after_start=1)
    _create_auction(pool, "auction-3", "200", kicked_hours_after_start=2)


def _get_uids(client, params):
    response = client.get(URL, params)

    assert response.status_code == 200
    return [row["uid"] for row in response.json()["results"]]


@pytest.mark.django_db
@pytest.mark.usefixtures("auctions")
@pytest.mark.parametrize(
    ("order", "expected"),
    [
        ("debt_remaining", ["auction-2", "auction-3", "auction-1"]),
        ("-debt_remaining", ["auction-1", "auction-3", "auction-2"]),
    ],
)
def test_auctions_active_order_by_debt_remaining(client, order, expected):
    assert _get_uids(client, {"order": order}) == expected


@pytest.mark.django_db
@pytest.mark.usefixtures("auctions")
@pytest.mark.parametrize("order", ["debt", "-debt"])
def test_auctions_active_ignores_ambiguous_order(client, order):
    assert _get_uids(client, {"order": order}) == ["auction-3", "auction-2", "auction-1"]
