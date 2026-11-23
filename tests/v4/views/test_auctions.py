from datetime import UTC, datetime, timedelta

import factory
import pytest

from ajna.v4.base.chain import MODEL_MAP
from tests.factories import PoolFactory
from tests.helpers import create_active_auction, get_result_uids

URL = "/v4/base/auctions/active/"
FIRST_KICK_TIME = datetime(2026, 1, 1, tzinfo=UTC)


@pytest.fixture
def auctions():
    pool = factory.create(MODEL_MAP["pool"], FACTORY_CLASS=PoolFactory)
    for hours, (uid, debt_remaining) in enumerate(
        [("auction-1", 300), ("auction-2", 100), ("auction-3", 200)]
    ):
        create_active_auction(
            MODEL_MAP,
            pool.address,
            uid,
            FIRST_KICK_TIME + timedelta(hours=hours),
            debt_remaining=debt_remaining,
        )


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
    assert get_result_uids(client, URL, {"order": order}) == expected


@pytest.mark.django_db
@pytest.mark.usefixtures("auctions")
@pytest.mark.parametrize("order", ["debt", "-debt"])
def test_auctions_active_ignores_ambiguous_order(client, order):
    assert get_result_uids(client, URL, {"order": order}) == ["auction-3", "auction-2", "auction-1"]
