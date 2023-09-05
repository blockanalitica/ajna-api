from datetime import date, datetime, timedelta
from decimal import Decimal

from ajna.constants import SECONDS_PER_YEAR


def unwrap_symbol(symbol):
    return symbol[1:]


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def decode_bytes(value):
    return value.decode("utf-8").rstrip("\x00")


def timestamp_to_full_hour(dt):
    dt = dt.replace(second=0, microsecond=0, minute=0, hour=dt.hour)
    return int(datetime.timestamp(dt))


def get_percentage_difference(x, y):
    if x == 0 and y == 0:
        return 0
    if (x == 0 and y > 0) or (y == 0 and x > 0):
        return 100
    return abs(x - y) / ((x + y) / 2) * 100


def apr_to_apy(value, compounds=SECONDS_PER_YEAR):
    return pow((1 + value / Decimal(compounds)), Decimal(compounds)) - 1


def date_to_timestamp(dt):
    from_datetime = datetime(year=dt.year, month=dt.month, day=dt.day)
    return int(datetime.timestamp(from_datetime))


def get_today_timestamp():
    today = date.today()
    return date_to_timestamp(today)


def get_date_days_ago(number_of_days, start_date=None):
    if not start_date:
        start_date = date.today()
    dt = start_date - timedelta(days=number_of_days)
    return date(year=dt.year, month=dt.month, day=dt.day)


def yesterday_date():
    return date.today() - timedelta(days=1)


def datetime_to_full_hour(dt):
    dt = dt.replace(second=0, microsecond=0, minute=0, hour=dt.hour)
    return dt


def datetime_to_next_full_hour(dt):
    dt = dt.replace(second=0, microsecond=0, minute=0, hour=dt.hour) + timedelta(
        hours=1
    )
    return dt


def compute_order_index(block_number, tx_index, log_index):
    return "_".join(
        (str(block_number).zfill(12), str(tx_index).zfill(6), str(log_index).zfill(6))
    )
