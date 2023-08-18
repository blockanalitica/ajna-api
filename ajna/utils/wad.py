from decimal import Decimal


def wad_to_decimal(wad):
    return Decimal(str(wad)) / Decimal("1e18")
