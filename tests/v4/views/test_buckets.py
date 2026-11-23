import factory
import pytest

from ajna.v4.ethereum.chain import MODEL_MAP
from tests.factories import BucketFactory, PoolFactory, TokenFactory


@pytest.fixture
def bucket():
    collateral_token = factory.create(MODEL_MAP["token"], FACTORY_CLASS=TokenFactory)
    quote_token = factory.create(MODEL_MAP["token"], FACTORY_CLASS=TokenFactory)
    pool = factory.create(
        MODEL_MAP["pool"],
        FACTORY_CLASS=PoolFactory,
        collateral_token_address=collateral_token.underlying_address,
        quote_token_address=quote_token.underlying_address,
    )
    return factory.create(
        MODEL_MAP["bucket"],
        FACTORY_CLASS=BucketFactory,
        pool_address=pool.address,
        bucket_index=4156,
    )


@pytest.mark.django_db
def test_bucket_returns_bucket(client, bucket):
    response = client.get(f"/v4/ethereum/pools/{bucket.pool_address}/buckets/4156/")

    assert response.status_code == 200
    assert response.json()["bucket_index"] == 4156


@pytest.mark.django_db
@pytest.mark.parametrize("suffix", ["", "depositors/", "historic/", "events/"])
@pytest.mark.parametrize("bucket_index", ["notanint", "-1", "9" * 27])
def test_bucket_routes_reject_invalid_bucket_index(client, bucket, suffix, bucket_index):
    response = client.get(
        f"/v4/ethereum/pools/{bucket.pool_address}/buckets/{bucket_index}/{suffix}"
    )

    assert response.status_code == 404
