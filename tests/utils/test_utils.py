import pytest

from ajna.utils.utils import compute_order_index


@pytest.mark.parametrize(
    ("block_number", "tx_index", "log_index", "expected"),
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
