from decimal import Decimal

import pytest

from ajna.utils.wad import wad_to_decimal


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
