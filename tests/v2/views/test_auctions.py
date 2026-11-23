from datetime import UTC, datetime, timedelta

import factory
import pytest

from ajna.v2.ethereum.chain import MODEL_MAP
from tests.factories import PoolFactory
from tests.helpers import create_active_auction, get_result_uids

FIRST_KICK_TIME = datetime(2026, 1, 1, tzinfo=UTC)
DEFAULT_ORDER = ["auction-2", "auction-1", "auction-3"]


@pytest.fixture
def pool():
    return factory.create(MODEL_MAP["pool"], FACTORY_CLASS=PoolFactory)


@pytest.fixture(params=["global", "pool"])
def url(request, pool):
    if request.param == "global":
        return "/v2/ethereum/auctions/active/"
    return f"/v2/ethereum/pools/{pool.address}/auctions/active/"


@pytest.fixture
def auctions(pool):
    for hours, (uid, collateral_remaining, debt_remaining) in enumerate(
        [("auction-1", 2, 300), ("auction-2", 3, 100), ("auction-3", 1, 200)]
    ):
        create_active_auction(
            MODEL_MAP,
            pool.address,
            uid,
            FIRST_KICK_TIME + timedelta(hours=hours),
            collateral_remaining=collateral_remaining,
            debt_remaining=debt_remaining,
        )


@pytest.mark.django_db
@pytest.mark.usefixtures("auctions")
@pytest.mark.parametrize(
    ("order", "expected"),
    [
        (None, DEFAULT_ORDER),
        ("collateral_remaining", ["auction-3", "auction-1", "auction-2"]),
        ("-debt_remaining", ["auction-1", "auction-3", "auction-2"]),
        ("kick_time", ["auction-1", "auction-2", "auction-3"]),
    ],
)
def test_auctions_active_order(client, url, order, expected):
    params = {"order": order} if order else {}

    assert get_result_uids(client, url, params) == expected


@pytest.mark.django_db
@pytest.mark.usefixtures("auctions")
@pytest.mark.parametrize("order", ["collateral", "-collateral", "debt", "-debt"])
def test_auctions_active_ignores_ambiguous_order(client, url, order):
    assert get_result_uids(client, url, {"order": order}) == DEFAULT_ORDER
