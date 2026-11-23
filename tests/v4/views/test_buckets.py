import factory
import pytest

from ajna.v4.ethereum.models import V3EthereumBucket, V3EthereumPool, V3EthereumToken
from tests.factories import BucketFactory, PoolFactory, TokenFactory


class EthereumPoolFactory(PoolFactory):
    class Meta:
        model = V3EthereumPool


class EthereumTokenFactory(TokenFactory):
    class Meta:
        model = V3EthereumToken


class EthereumBucketFactory(BucketFactory):
    class Meta:
        model = V3EthereumBucket

    pool_address = factory.Faker("ethereum_address")


@pytest.fixture
def bucket():
    collateral_token = EthereumTokenFactory()
    quote_token = EthereumTokenFactory()
    pool = EthereumPoolFactory(
        collateral_token_address=collateral_token.underlying_address,
        quote_token_address=quote_token.underlying_address,
    )
    return EthereumBucketFactory(pool_address=pool.address, bucket_index=4156)


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
