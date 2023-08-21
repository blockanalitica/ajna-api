from decimal import Decimal, ROUND_CEILING


def wad_to_decimal(wad):
    if not wad:
        wad = "0"
    return Decimal(str(wad)) / Decimal("1e18")


def round_ceil(num):
    assert isinstance(num, Decimal)
    return num.quantize(Decimal(".000000000000000001"), rounding=ROUND_CEILING)
