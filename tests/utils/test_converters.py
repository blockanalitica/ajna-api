import pytest

from ajna.utils.converters import BIGINT_MAX, BucketIndexConverter


@pytest.mark.parametrize("value", ["0", "4156", str(BIGINT_MAX)])
def test_bucket_index_converter_accepts_bigint(value):
    assert BucketIndexConverter().to_python(value) == int(value)


def test_bucket_index_converter_rejects_values_above_bigint():
    with pytest.raises(ValueError, match="out of range"):
        BucketIndexConverter().to_python(str(BIGINT_MAX + 1))


def test_bucket_index_converter_to_url():
    assert BucketIndexConverter().to_url(4156) == "4156"
