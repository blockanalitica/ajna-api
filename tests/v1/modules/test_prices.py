from decimal import Decimal

import pytest
import responses

from ajna.v1.ethereum import models
from ajna.v1.modules.prices import update_token_prices
from tests.v1.factories import V1TokenFactory


@pytest.mark.django_db
@responses.activate
def test_update_token_prices():
    """
    Test update_token_prices function to ensure proper updating of underlying_price.

    This test checks that the update_token_prices function:
    1. Fetches the current prices for tokens from the mocked API.
    2. Updates the underlying_price field for all Token instances in the database.
    """

    # Create tokens using the TokenFactory
    token_1 = V1TokenFactory()
    token_2 = V1TokenFactory()
    token_3 = V1TokenFactory()

    # Mock response for get_current_prices
    mock_response = {
        "coins": {
            f"ethereum:{token_1.underlying_address}": {
                "decimals": 6,
                "symbol": f"{token_1.symbol}",
                "price": 1,
                "timestamp": 1680029580,
                "confidence": 0.99,
            },
            f"ethereum:{token_2.underlying_address}": {
                "decimals": 18,
                "symbol": f"{token_2.symbol}",
                "price": 1000,
                "timestamp": 1680029580,
                "confidence": 0.99,
            },
            f"ethereum:{token_3.underlying_address}": {
                "decimals": 18,
                "symbol": f"{token_3.symbol}",
                "price": 0.089,
                "timestamp": 1680029580,
                "confidence": 0.99,
            },
        }
    }
    token_model = models.V1EthereumToken
    price_feed_model = models.V1EthereumPriceFeed
    addresses = token_model.objects.all().values_list("underlying_address", flat=True)
    coins = [f"ethereum:{address}" for address in addresses]
    external_api_url = "https://coins.llama.fi/prices/current/{}/".format(
        ",".join(coins)
    )
    responses.add(
        responses.GET,
        external_api_url,
        json=mock_response,
        status=200,
        content_type="application/json",
    )

    update_token_prices(models)

    # Assert that the underlying_price field has been updated for tokens
    assert token_model.objects.get(
        underlying_address=token_1.underlying_address
    ).underlying_price == Decimal("1")
    assert token_model.objects.get(
        underlying_address=token_2.underlying_address
    ).underlying_price == Decimal("1000")
    assert token_model.objects.get(
        underlying_address=token_3.underlying_address
    ).underlying_price == Decimal("0.089")

    assert price_feed_model.objects.count() == 3
