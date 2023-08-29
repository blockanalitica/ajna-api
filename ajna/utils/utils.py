from datetime import datetime, timedelta
from decimal import Decimal, ROUND_CEILING


def date_to_timestamp(dt):
    from_datetime = datetime(year=dt.year, month=dt.month, day=dt.day)
    return int(datetime.timestamp(from_datetime))


def datetime_to_full_hour(dt):
    dt = dt.replace(second=0, microsecond=0, minute=0, hour=dt.hour)
    return dt


def datetime_to_next_full_hour(dt):
    dt = dt.replace(second=0, microsecond=0, minute=0, hour=dt.hour) + timedelta(
        hours=1
    )
    return dt


def wad_to_decimal(wad):
    if not wad:
        wad = "0"
    return Decimal(str(wad)) / Decimal("1e18")


def round_ceil(num):
    assert isinstance(num, Decimal)
    return num.quantize(Decimal(".000000000000000001"), rounding=ROUND_CEILING)


def compute_order_index(block_number, tx_index, log_index):
    return "_".join(
        (str(block_number).zfill(12), str(tx_index).zfill(6), str(log_index).zfill(6))
    )
