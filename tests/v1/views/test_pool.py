import pytest
from django.urls import reverse

from tests.v1.factories import V1BucketFactory, V1PoolFactory, V1TokenFactory


@pytest.mark.django_db
def test_pool(client):
    """
    Test the pool list endpoint to ensure it returns the correct data.

    This test creates a collateral and a quote token using V1TokenFactory, then
    creates a pool using V1PoolFactory with the created tokens as collateral_token_address
    and quote_token_address. It then sends a GET request to the pool list endpoint using
    the pool address and asserts that the response has a 200 status code and the correct
    pool address in the response data.

    """
    collateral_token = V1TokenFactory.create()
    quote_token = V1TokenFactory.create()

    pool = V1PoolFactory.create(
        collateral_token_address=collateral_token.underlying_address,
        quote_token_address=quote_token.underlying_address,
    )

    response = client.get(
        reverse("v1_ethereum:pool", kwargs={"pool_address": pool.address})
    )

    # Assert that the response has a 200 status code (OK)
    assert response.status_code == 200

    assert response.data["results"]["address"] == pool.address


@pytest.mark.django_db
def test_pool__404(client):
    """
    Test the pool endpoint to ensure it returns a 404 status code for an invalid pool address.

    This test sends a GET request to the pool endpoint using an invalid pool address ('0xwrong')
    and asserts that the response has a 404 status code (Not Found).

    """

    response = client.get(
        reverse("v1_ethereum:pool", kwargs={"pool_address": "0xwrong"})
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_buckets(client):
    """
    Test the buckets endpoint to ensure that it returns the correct number
    of buckets associated with a specific pool address.

    This test creates a pool and three associated buckets. It then sends a GET
    request to the "v1_ethereum:pool-buckets" endpoint with the pool address
    and checks if the response has a 200 status code (OK) and if the correct
    number of buckets (3) is returned in the response.
    """
    collateral_token = V1TokenFactory.create()
    quote_token = V1TokenFactory.create()

    pool = V1PoolFactory.create(
        collateral_token_address=collateral_token.underlying_address,
        quote_token_address=quote_token.underlying_address,
    )

    V1BucketFactory.create_batch(3, pool_address=pool.address)

    response = client.get(
        reverse("v1_ethereum:pool-buckets", kwargs={"pool_address": pool.address})
    )

    # Assert that the response has a 200 status code (OK)
    assert response.status_code == 200
    assert len(response.data["results"]) == 3
