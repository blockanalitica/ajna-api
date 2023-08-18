from decimal import Decimal


def wad_to_decimal(wad):
    if not wad:
        wad = "0"
    return Decimal(str(wad)) / Decimal("1e18")
