from decimal import Decimal

import pytest
import responses

from ajna.v1.ethereum.chain import EthereumModels
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
    token_1 = V1TokenFactory(symbol="WBTC")
    token_2 = V1TokenFactory()
    token_3 = V1TokenFactory()
    token_4 = V1TokenFactory(
        symbol="YieldBTC",
        underlying_address="0x0274a704a6d9129f90a62ddc6f6024b33ecdad36",
    )

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
    models = EthereumModels()
    addresses = models.token.objects.all().values_list("underlying_address", flat=True)
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

    external_rhino_url = "https://api.stg.rhino.fi/market-data/ticker/YIELDBTC:BTC"
    responses.add(
        responses.GET,
        external_rhino_url,
        json=[0, 0, 0, 0, 0, 0, 1.4, 0, 0, 0],
        status=200,
        content_type="application/json",
    )

    update_token_prices(models)

    # Assert that the underlying_price field has been updated for tokens
    assert models.token.objects.get(
        underlying_address=token_1.underlying_address
    ).underlying_price == Decimal("1")
    assert models.token.objects.get(
        underlying_address=token_2.underlying_address
    ).underlying_price == Decimal("1000")
    assert models.token.objects.get(
        underlying_address=token_3.underlying_address
    ).underlying_price == Decimal("0.089")
    assert models.token.objects.get(
        underlying_address=token_4.underlying_address
    ).underlying_price == Decimal("1.4")
    assert models.token.objects.count() == 4
