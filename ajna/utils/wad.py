from decimal import ROUND_HALF_UP, Decimal


def wad_to_decimal(wad):
    if not wad:
        wad = "0"

    return Decimal(str(wad)) / Decimal("1e18")


def decimal_to_wad(value):
    value = value.quantize(Decimal(".000000000000000001"), rounding=ROUND_HALF_UP)
    wad = value * Decimal("1e18")
    return int(wad)
