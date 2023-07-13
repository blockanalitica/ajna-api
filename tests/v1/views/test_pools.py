import pytest
from django.urls import reverse

from tests.v1.factories import V1PoolFactory, V1TokenFactory


@pytest.mark.django_db
def test_pools(client):
    """
    Test the pool list endpoint to ensure it returns the correct data.

    This test creates a collateral and a quote token using V1TokenFactory, then
    creates 3 pools using V1PoolFactory with the created tokens as collateral_token_address
    and quote_token_address. It then sends a GET request to the pool list endpoint and
    asserts that the response has a 200 status code, contains the expected number of pools,
    and has the correct information in the response data.
    """
    collateral_token = V1TokenFactory.create()
    quote_token = V1TokenFactory.create()

    V1PoolFactory.create_batch(
        3,
        collateral_token_address=collateral_token.underlying_address,
        quote_token_address=quote_token.underlying_address,
    )

    response = client.get(reverse("v1_ethereum:pools"))

    # Assert that the response has a 200 status code (OK)
    assert response.status_code == 200

    # Assert that the response contains the expected number of pools
    assert response.data["count"] == 3
    assert len(response.data["results"]) == 3

    # Assert that the response data contains the correct information
    for pool in response.data["results"]:
        assert pool["collateral_token_symbol"] == collateral_token.symbol
        assert pool["quote_token_symbol"] == quote_token.symbol
