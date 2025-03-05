import logging
from datetime import datetime
from decimal import Decimal

from ajna.sources.defillama import get_current_prices

log = logging.getLogger(__name__)

RHINOFI_MAP = {
    "0x0274a704a6d9129f90a62ddc6f6024b33ecdad36": {
        "rhino_pair": "YIELDBTC:BTC",
        "price_token": "WBTC",
    }
}


def _save_price_for_address(models, address, price):
    models.token.objects.filter(underlying_address=address).update(underlying_price=price)
    try:
        price_feed = models.price_feed.objects.filter(underlying_address=address).latest()
    except models.price_feed.DoesNotExist:
        price_feed = None

    dt = datetime.now()
    if price_feed is None or price_feed.price != price:
        models.price_feed.objects.create(
            underlying_address=address,
            price=price,
            datetime=dt,
            timestamp=dt.timestamp(),
        )


def _handle_rhinofi_tokens(models, done_addresses, chain):
    for address, data in RHINOFI_MAP.items():
        if address in done_addresses:
            log.debug("Skipping {} address from rhino.fi price fetching")
            continue

        burn_data_calls = [
            (
                address,
                [
                    "convertToAssets(uint256)(uint256)",
                    1 * (10**18),
                ],
                ["assets", None],
            ),
        ]
        on_chain_data = chain.multicall(burn_data_calls)
        # the only token we check here is YIELDBTC and we know it has 8 decimal precision
        conversion_rate = Decimal(str(on_chain_data["assets"])) / 10**8
        price_token = models.token.objects.get(symbol=data["price_token"])

        price = price_token.underlying_price * conversion_rate
        _save_price_for_address(models, address, price)


def update_token_prices(chain):
    """
    Updates the underlying_price field for all Token instances in the database.

    This function retrieves all the underlying addresses of the tokens, fetches the
    current prices for those addresses, and then updates the corresponding token
    instances with the new prices.
    """
    underlying_addresses = chain.token.objects.all().values_list("underlying_address", flat=True)
    if not underlying_addresses:
        return
    prices_mapping = get_current_prices(underlying_addresses)

    done_addresses = set()
    for key, values in prices_mapping.items():
        _, underlying_address = key.split(":")
        done_addresses.add(underlying_addresses)

        price = Decimal(str(values["price"]))
        _save_price_for_address(chain, underlying_address, price)

    _handle_rhinofi_tokens(chain, done_addresses, chain)
