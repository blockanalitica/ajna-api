from decimal import Decimal

import pytest
from django.urls import reverse

from ajna.v1.ethereum.models import V1EthereumToken
from tests.v1.factories import V1PoolFactory, V1TokenFactory


@pytest.mark.django_db
def test_tokens_view(client):
    """
    This test function verifies the behavior of the TokensView API endpoint. It creates sample
    tokens and associated pools, and then sends a GET request to the endpoint. It checks if the
    response contains the correct information, such as the token details and the count of
    associated pools.
    """
    # Create sample tokens and pools
    tokens = V1TokenFactory.create_batch(3)
    for token in tokens:
        V1PoolFactory.create(
            collateral_token_address=token.underlying_address,
            quote_token_address=V1TokenFactory.create().underlying_address,
        )

    tokens = V1EthereumToken.objects.all()

    response = client.get(reverse("v1_ethereum:tokens"))

    # Assert that the response has a 200 status code (OK)
    assert response.status_code == 200

    # Assert that the response contains the expected number of tokens
    assert response.data["count"] == 6

    # Assert that the response data contains the correct information
    for token_data in response.data["results"]:
        token = next(
            t
            for t in tokens
            if t.underlying_address == token_data["underlying_address"]
        )
        assert token_data["symbol"] == token.symbol
        assert token_data["name"] == token.name
        assert token_data["underlying_price"] == Decimal(str(token.underlying_price))
        assert token_data["pool_count"] == 1
