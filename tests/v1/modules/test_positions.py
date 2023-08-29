from collections import defaultdict
from datetime import datetime
from decimal import Decimal

import pytest

from ajna.v1.ethereum.chain import Ethereum
from ajna.v1.modules.positions import (
    _handle_collateral_events,
    _handle_debt_events,
    _handle_quote_token_events,
    save_wallet_positions,
)
from tests.utils import generate_ethereum_address
from tests.v1.factories import (
    V1AddCollateralFactory,
    V1AddQuoteTokenFactory,
    V1DrawDebtFactory,
    V1MoveQuoteTokenFactory,
    V1RemoveCollateralFactory,
    V1RemoveQuoteTokenFactory,
    V1RepayDebtFactory,
)


@pytest.fixture
def dummy_models(db):
    wallet_address = generate_ethereum_address()
    pool_address_1 = generate_ethereum_address()
    pool_address_2 = generate_ethereum_address()

    V1DrawDebtFactory(block_number=17732900)  # random pool/wallet
    V1DrawDebtFactory(
        pool_address=pool_address_1,
        borrower=wallet_address,
        block_number=17732900,
        amount_borrowed=Decimal("100"),
        collateral_pledged=Decimal("50"),
    )
    V1DrawDebtFactory(
        pool_address=pool_address_2,
        borrower=wallet_address,
        block_number=17732900,
        amount_borrowed=Decimal("110"),
        collateral_pledged=Decimal("80"),
    )
    V1DrawDebtFactory(
        pool_address=pool_address_1,
        borrower=wallet_address,
        block_number=17732901,
        amount_borrowed=Decimal("200"),
        collateral_pledged=Decimal("100"),
    )
    V1DrawDebtFactory(
        pool_address=pool_address_2,
        block_number=17732902,
    )

    V1RepayDebtFactory(
        pool_address=pool_address_1,
        borrower=wallet_address,
        block_number=17732901,
        quote_repaid=Decimal("50"),
        collateral_pulled=Decimal("25"),
    )
    V1RepayDebtFactory(
        pool_address=pool_address_1,
        borrower=wallet_address,
        block_number=17732902,
        quote_repaid=Decimal("25"),
        collateral_pulled=Decimal("10"),
    )

    V1AddQuoteTokenFactory(block_number=17732900)  # random pool/wallet
    V1AddQuoteTokenFactory(
        pool_address=pool_address_1,
        lender=wallet_address,
        block_number=17732900,
        amount=Decimal("100"),
    )

    V1AddQuoteTokenFactory(
        pool_address=pool_address_2,
        lender=wallet_address,
        block_number=17732900,
        amount=Decimal("111"),
    )

    V1RemoveQuoteTokenFactory(
        pool_address=pool_address_1,
        lender=wallet_address,
        block_number=17732901,
        amount=Decimal("20"),
    )

    V1AddQuoteTokenFactory(
        pool_address=pool_address_1,
        lender=wallet_address,
        block_number=17732902,
        amount=Decimal("50"),
    )

    V1MoveQuoteTokenFactory(
        pool_address=pool_address_1,
        lender=wallet_address,
        block_number=17732902,
        amount=Decimal("20"),
    )

    V1AddQuoteTokenFactory(
        pool_address=pool_address_1,
        lender=wallet_address,
        block_number=17732902,
        amount=Decimal("70"),
    )

    V1RemoveQuoteTokenFactory(
        pool_address=pool_address_1,
        lender=wallet_address,
        block_number=17732903,
        amount=Decimal("25"),
    )

    V1AddCollateralFactory(block_number=17732900)  # random pool/wallet
    V1RemoveCollateralFactory(
        pool_address=pool_address_1, block_number=17732900
    )  # random pool
    V1AddCollateralFactory(
        pool_address=pool_address_1,
        actor=wallet_address,
        block_number=17732901,
        amount=Decimal("7"),
    )

    V1RemoveCollateralFactory(
        pool_address=pool_address_1,
        block_number=17732902,
        claimer=wallet_address,
        amount=Decimal("4"),
    )

    V1AddCollateralFactory(
        pool_address=pool_address_2,
        actor=wallet_address,
        block_number=17732901,
        amount=Decimal("4"),
    )

    V1RemoveCollateralFactory(
        pool_address=pool_address_2,
        block_number=17732902,
        claimer=wallet_address,
        amount=Decimal("4"),
    )

    yield wallet_address, pool_address_1, pool_address_2


@pytest.mark.django_db
def test_handle_debt_events(dummy_models, monkeypatch):
    wallet_address, pool_address_1, pool_address_2 = dummy_models
    chain = Ethereum()

    monkeypatch.setattr(
        chain,
        "multicall",
        lambda calls, block_id: {
            pool_address_1: (
                1,
                2,
                "3",
                1000338271841430976,
                5,
            ),
            pool_address_2: (
                1,
                2,
                "3",
                1000351015701187583,
                5,
            ),
        },
    )

    positions = defaultdict(lambda: defaultdict(Decimal))

    _handle_debt_events(chain, wallet_address, 0, positions)

    assert len(positions) == 2

    # Make sure we only update debt related fields
    assert list(positions[pool_address_1].keys()) == [
        "debt",
        "t0debt",
        "collateral",
        "block_number",
        "datetime",
    ]
    assert positions[pool_address_1]["debt"] == Decimal("225")
    assert positions[pool_address_1]["t0debt"] == Decimal("224.923914573235448107")
    assert positions[pool_address_1]["collateral"] == Decimal("115")
    assert positions[pool_address_1]["block_number"] == 17732902
    assert positions[pool_address_1]["datetime"] == datetime(2023, 6, 11, 12, 43, 21)

    assert list(positions[pool_address_2].keys()) == [
        "debt",
        "t0debt",
        "collateral",
        "block_number",
        "datetime",
    ]
    assert positions[pool_address_2]["debt"] == Decimal("110")
    assert positions[pool_address_2]["t0debt"] == Decimal("109.961401821436079048")
    assert positions[pool_address_2]["collateral"] == Decimal("80")
    assert positions[pool_address_2]["block_number"] == 17732900
    assert positions[pool_address_2]["datetime"] == datetime(2023, 6, 11, 12, 42, 53)


@pytest.mark.django_db
def test_handle_quote_token_events(dummy_models):
    wallet_address, pool_address_1, pool_address_2 = dummy_models
    chain = Ethereum()

    positions = defaultdict(lambda: defaultdict(Decimal))

    _handle_quote_token_events(chain, wallet_address, 0, positions)

    assert len(positions) == 2

    # Make sure we only update debt related fields
    assert list(positions[pool_address_1].keys()) == [
        "supply",
        "block_number",
        "datetime",
    ]
    assert positions[pool_address_1]["supply"] == Decimal("175")
    assert positions[pool_address_1]["block_number"] == 17732903
    assert positions[pool_address_1]["datetime"] == datetime(2023, 6, 11, 12, 43, 35)

    assert list(positions[pool_address_2].keys()) == [
        "supply",
        "block_number",
        "datetime",
    ]
    assert positions[pool_address_2]["supply"] == Decimal("111")
    assert positions[pool_address_2]["block_number"] == 17732900
    assert positions[pool_address_2]["datetime"] == datetime(2023, 6, 11, 12, 42, 53)


@pytest.mark.django_db
def test_handle_collateral_events(dummy_models):
    wallet_address, pool_address_1, pool_address_2 = dummy_models
    chain = Ethereum()

    positions = defaultdict(lambda: defaultdict(Decimal))

    _handle_collateral_events(chain, wallet_address, 0, positions)

    assert len(positions) == 2

    # Make sure we only update debt related fields
    assert list(positions[pool_address_1].keys()) == [
        "collateral",
        "block_number",
        "datetime",
    ]
    assert positions[pool_address_1]["collateral"] == Decimal("3")
    assert positions[pool_address_1]["block_number"] == 17732902
    assert positions[pool_address_1]["datetime"] == datetime(2023, 6, 11, 12, 43, 21)

    assert list(positions[pool_address_2].keys()) == [
        "collateral",
        "block_number",
        "datetime",
    ]
    assert positions[pool_address_2]["supply"] == Decimal("0")
    assert positions[pool_address_2]["block_number"] == 17732902
    assert positions[pool_address_2]["datetime"] == datetime(2023, 6, 11, 12, 43, 21)


@pytest.mark.django_db
def test_save_wallet_positions(dummy_models, monkeypatch):
    wallet_address, pool_address_1, pool_address_2 = dummy_models
    chain = Ethereum()
    monkeypatch.setattr(
        chain,
        "multicall",
        lambda calls, block_id: {
            pool_address_1: (
                1,
                2,
                "3",
                1000338271841430976,
                5,
            ),
            pool_address_2: (
                1,
                2,
                "3",
                1000351015701187583,
                5,
            ),
        },
    )

    save_wallet_positions(chain, wallet_address, 0)

    positions = chain.current_position.objects.all().order_by("block_number")

    assert len(positions) == 2

    assert positions[0].wallet_address == wallet_address
    assert positions[0].pool_address == pool_address_2
    assert positions[0].debt == Decimal("110")
    assert positions[0].t0debt == Decimal("109.961401821436079048")
    assert positions[0].collateral == Decimal("80")
    assert positions[0].supply == Decimal("111")
    assert positions[0].block_number == 17732902
    assert positions[0].datetime == datetime(2023, 6, 11, 12, 43, 21)

    assert positions[1].wallet_address == wallet_address
    assert positions[1].pool_address == pool_address_1
    assert positions[1].debt == Decimal("225")
    assert positions[1].t0debt == Decimal("224.923914573235448107")
    assert positions[1].collateral == Decimal("118")
    assert positions[1].supply == Decimal("175")
    assert positions[1].block_number == 17732903
    assert positions[1].datetime == datetime(2023, 6, 11, 12, 43, 35)
