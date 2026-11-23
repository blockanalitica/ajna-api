from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from ajna.v2.ethereum.models import V2EthereumAuction, V2EthereumAuctionKick, V2EthereumPool
from tests.factories import PoolFactory

BORROWER = "0x5c9d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d"
FIRST_KICK_TIME = datetime(2026, 1, 1, tzinfo=UTC)


class EthereumPoolFactory(PoolFactory):
    class Meta:
        model = V2EthereumPool


@pytest.fixture
def pool():
    return EthereumPoolFactory()


@pytest.fixture(params=["global", "pool"])
def url(request, pool):
    if request.param == "global":
        return "/v2/ethereum/auctions/active/"
    return f"/v2/ethereum/pools/{pool.address}/auctions/active/"


def _create_auction(pool, uid, collateral_remaining, debt_remaining, kicked_hours_after_start):
    auction = V2EthereumAuction.objects.create(
        uid=uid,
        pool_address=pool.address,
        borrower=BORROWER,
        collateral=Decimal(10),
        collateral_remaining=Decimal(collateral_remaining),
        debt=Decimal(100),
        debt_remaining=Decimal(debt_remaining),
    )
    V2EthereumAuctionKick.objects.create(
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
def auctions(pool):
    _create_auction(pool, "auction-1", "2", "300", kicked_hours_after_start=0)
    _create_auction(pool, "auction-2", "3", "100", kicked_hours_after_start=1)
    _create_auction(pool, "auction-3", "1", "200", kicked_hours_after_start=2)


def _get_uids(client, url, params):
    response = client.get(url, params)

    assert response.status_code == 200
    return [row["uid"] for row in response.json()["results"]]


@pytest.mark.django_db
@pytest.mark.usefixtures("auctions")
@pytest.mark.parametrize(
    ("order", "expected"),
    [
        (None, ["auction-2", "auction-1", "auction-3"]),
        ("collateral_remaining", ["auction-3", "auction-1", "auction-2"]),
        ("-debt_remaining", ["auction-1", "auction-3", "auction-2"]),
        ("kick_time", ["auction-1", "auction-2", "auction-3"]),
    ],
)
def test_auctions_active_order(client, url, order, expected):
    params = {"order": order} if order else {}

    assert _get_uids(client, url, params) == expected


@pytest.mark.django_db
@pytest.mark.usefixtures("auctions")
@pytest.mark.parametrize("order", ["collateral", "-collateral", "debt", "-debt"])
def test_auctions_active_ignores_ambiguous_order(client, url, order):
    assert _get_uids(client, url, {"order": order}) == ["auction-2", "auction-1", "auction-3"]
