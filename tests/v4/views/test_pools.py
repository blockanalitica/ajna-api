from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from ajna.v4.base.models import V4BaseAuction, V4BaseAuctionKick, V4BasePool

POOL_ADDRESS = "0x2a1b5a5b0b7b5e4b9b2f3a1c6d5e4f3a2b1c0d9e"
BORROWER = "0x5c9d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d"
FIRST_KICK_TIME = datetime(2026, 1, 1, tzinfo=UTC)
URL = f"/v4/base/pools/{POOL_ADDRESS}/auctions/active/"


@pytest.fixture
def pool():
    return V4BasePool.objects.create(
        address=POOL_ADDRESS,
        pool_size=Decimal("0"),
        debt=Decimal("0"),
        inflator=Decimal("0"),
        borrow_rate=Decimal("0"),
        pledged_collateral=Decimal("0"),
        total_interest_earned=Decimal("0"),
        loans_count=0,
        hpb=Decimal("0"),
        hpb_index=0,
        htp=Decimal("0"),
        htp_index=0,
        lup=Decimal("0"),
        lup_index=0,
        reserves=Decimal("0"),
        claimable_reserves=Decimal("0"),
        claimable_reserves_remaining=Decimal("0"),
        burn_epoch=0,
        min_debt_amount=Decimal("0"),
        actual_utilization=Decimal("0"),
        target_utilization=Decimal("0"),
        datetime=FIRST_KICK_TIME,
        created_at_block_number=0,
        created_at_timestamp=0,
    )


def _create_auction(pool, uid, debt_remaining, kicked_hours_after_start):
    kick_time = FIRST_KICK_TIME + timedelta(hours=kicked_hours_after_start)
    auction = V4BaseAuction.objects.create(
        uid=uid,
        pool_address=pool.address,
        borrower=BORROWER,
        collateral=Decimal("10"),
        collateral_remaining=Decimal("10"),
        debt=Decimal("100"),
        debt_remaining=Decimal(debt_remaining),
    )
    V4BaseAuctionKick.objects.create(
        order_index=uid,
        auction_uid=auction.uid,
        pool_address=pool.address,
        borrower=BORROWER,
        kicker=BORROWER,
        debt=Decimal("100"),
        collateral=Decimal("10"),
        bond=Decimal("1"),
        locked=Decimal("0"),
        starting_price=Decimal("1"),
        block_number=kicked_hours_after_start + 1,
        block_datetime=kick_time,
    )


def _get_uids(client, params):
    response = client.get(URL, params)

    assert response.status_code == 200
    return [row["uid"] for row in response.json()["results"]]


@pytest.mark.django_db
def test_auctions_active_order_by_debt_remaining(client, pool):
    # kick time order (the default) is the reverse of the debt_remaining order
    _create_auction(pool, "auction-1", "300", kicked_hours_after_start=0)
    _create_auction(pool, "auction-2", "100", kicked_hours_after_start=1)
    _create_auction(pool, "auction-3", "200", kicked_hours_after_start=2)

    assert _get_uids(client, {"order": "debt_remaining"}) == [
        "auction-2",
        "auction-3",
        "auction-1",
    ]
    assert _get_uids(client, {"order": "-debt_remaining"}) == [
        "auction-1",
        "auction-3",
        "auction-2",
    ]


@pytest.mark.django_db
@pytest.mark.parametrize("order", ["debt", "-debt"])
def test_auctions_active_order_by_unknown_field_does_not_error(client, pool, order):
    _create_auction(pool, "auction-1", "100", kicked_hours_after_start=0)

    # `debt` is not part of the active auctions payload, so it is ignored
    # instead of producing an ambiguous ORDER BY column
    assert _get_uids(client, {"order": order}) == ["auction-1"]
