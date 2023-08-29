from decimal import Decimal

import pytest

from ajna.utils.utils import wad_to_decimal, compute_order_index


@pytest.mark.parametrize(
    "wad,expected",
    [
        (67153818568173297, Decimal("0.067153818568173297")),
        ("888888888888888888", Decimal("0.888888888888888888")),
        ("1888888888888888888", Decimal("1.888888888888888888")),
        (69, Decimal("0.000000000000000069")),
        (6900000000000000000000, Decimal("6900")),
        (69000000000000000000001, Decimal("69000.000000000000000001")),
        (0, Decimal("0")),
        (None, Decimal("0")),
    ],
)
def test_wad_to_decimal(wad, expected):
    dec = wad_to_decimal(wad)
    assert isinstance(dec, Decimal)
    assert dec == expected


@pytest.mark.parametrize(
    "block_number,tx_index,log_index,expected",
    [
        (17684000, 66, 123, "000017684000_000066_000123"),
        (1, 2, 3, "000000000001_000002_000003"),
        (666666666666, "2", "15", "666666666666_000002_000015"),
        ("1", 333333, 666666, "000000000001_333333_666666"),
    ],
)
def test_compute_order_index(block_number, tx_index, log_index, expected):
    order_index = compute_order_index(block_number, tx_index, log_index)
    assert order_index == expected
