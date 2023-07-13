from decimal import Decimal

import pytest
from django.urls import reverse

from tests.v1.factories import V1PoolFactory, V1TokenFactory


@pytest.mark.django_db
def test_token_view(client):
    """
    Tests the TokenView by creating a sample token, sending a GET request to
    the appropriate endpoint, and asserting that the response has a 200 status
    code (OK) and has the correct information in the response data.
    """
    # Create a sample token
    token = V1TokenFactory.create()

    # Make a request to the TokenView
    response = client.get(
        reverse(
            "v1_ethereum:token",
            kwargs={"underlying_address": token.underlying_address},
        )
    )

    # Assert that the response has a 200 status code (OK)
    assert response.status_code == 200

    # Assert that the response data contains the correct information
    token_data = response.data["results"]
    assert token_data["underlying_address"] == token.underlying_address
    assert token_data["symbol"] == token.symbol
    assert token_data["name"] == token.name
    assert token_data["decimals"] == token.decimals
    assert token_data["is_erc721"] == token.is_erc721
    assert token_data["underlying_price"] == Decimal(str(token.underlying_price))


@pytest.mark.django_db
def test_token_pools_view(client):
    """
    Tests the TokenPoolsView by creating a sample token and related pools,
    sending a GET request to the appropriate endpoint, and asserting that the
    response has a 200 status code (OK), contains the expected number of pools,
    and has the correct information in the response data.
    """
    # Create a sample token
    token = V1TokenFactory.create()
    token_2 = V1TokenFactory.create()

    # Create pools related to the token
    pools = V1PoolFactory.create_batch(
        2,
        collateral_token_address=token.underlying_address,
        quote_token_address=token_2.underlying_address,
    )
    pools += V1PoolFactory.create_batch(
        2,
        quote_token_address=token.underlying_address,
        collateral_token_address=token_2.underlying_address,
    )

    # Make a request to the TokenPoolsView
    response = client.get(
        reverse(
            "v1_ethereum:token-pools",
            kwargs={"underlying_address": token.underlying_address},
        )
    )

    # Assert that the response has a 200 status code (OK)
    assert response.status_code == 200

    # Assert that the response contains the expected number of pools
    assert len(response.data["results"]) == 4

    # Assert that the response data contains the correct information
    for pool_data in response.data["results"]:
        pool = next(p for p in pools if p.address == pool_data["address"])
        assert pool_data["address"] == pool.address
