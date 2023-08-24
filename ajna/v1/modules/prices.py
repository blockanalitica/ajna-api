import logging
from datetime import datetime
from decimal import Decimal

from ajna.sources.defillama import get_current_prices
from ajna.sources.rhinofi import fetch_pair_price

log = logging.getLogger(__name__)

RHINOFI_MAP = {
    "0x0274a704a6d9129f90a62ddc6f6024b33ecdad36": {
        "rhino_pair": "YIELDBTC:BTC",
        "price_token": "WBTC",
    }
}


def _save_price_for_address(models, address, price):
    models.token.objects.filter(underlying_address=address).update(
        underlying_price=price
    )
    try:
        price_feed = models.price_feed.objects.filter(
            underlying_address=address
        ).latest()
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


def _handle_rhinofi_tokens(models, done_addresses):
    for address, data in RHINOFI_MAP.items():
        if address in done_addresses:
            log.debug("Skipping {} address from rhino.fi price fetching")
            continue

        conversion_price = fetch_pair_price(data["rhino_pair"])
        price_token = models.token.objects.get(symbol=data["price_token"])

        print("lalalla", price_token.underlying_price, conversion_price)
        price = price_token.underlying_price * conversion_price
        _save_price_for_address(models, address, price)


def update_token_prices(models, network="ethereum"):
    """
    Updates the underlying_price field for all Token instances in the database.

    This function retrieves all the underlying addresses of the tokens, fetches the
    current prices for those addresses, and then updates the corresponding token
    instances with the new prices.
    """
    if network == "goerli":
        MAPPING_TO_ETHEREUM = {
            "0x9c09fe6b19174d838cae2c4fb5a4a311c4008441": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  # TWETH
            "0x10aa0cf12aab305bd77ad8f76c037e048b12513b": "0x6b175474e89094c44da98b954eedeac495271d0f",  # TDAI
            "0x7ccf0411c7932b99fc3704d68575250f032e3bb7": "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",  # WBTC
            "0x6fb5ef893d44f4f88026430d82d4ef269543cb23": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",  # USDC
            "0xb4fbf271143f4fbf7b91a5ded31805e42b2208d6": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  # WETH
            "0x11fe4b6ae13d2a6055c8d9cf65c55bac32b5d844": "0x6b175474e89094c44da98b954eedeac495271d0f",  # DAI
            "0x6320cd32aa674d2898a68ec82e869385fc5f7e2f": "0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0",  # wstETH
            "0x62bc478ffc429161115a6e4090f819ce5c50a5d9": "0xae78736cd615f374d3085123a210448e74fc6393",  # rETH
            "0xdf1742fe5b0bfc12331d8eaec6b478dfdbd31464": "0x6b175474e89094c44da98b954eedeac495271d0f",  # DAI
            "0x4f1ef08f55fbc2eeddd79ff820357e8d25e49793": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",  # TUSDC
        }
        MAPPING_TO_GOERLI = {
            "0x6b175474e89094c44da98b954eedeac495271d0f": [
                "0x10aa0cf12aab305bd77ad8f76c037e048b12513b",
                "0x11fe4b6ae13d2a6055c8d9cf65c55bac32b5d844",
                "0xdf1742fe5b0bfc12331d8eaec6b478dfdbd31464",
            ],  # DAI
            "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599": [
                "0x7ccf0411c7932b99fc3704d68575250f032e3bb7"
            ],  # WBTC
            "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": [
                "0x6fb5ef893d44f4f88026430d82d4ef269543cb23",
                "0x4f1ef08f55fbc2eeddd79ff820357e8d25e49793",
            ],  # USDC
            "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": [
                "0xb4fbf271143f4fbf7b91a5ded31805e42b2208d6",
                "0x9c09fe6b19174d838cae2c4fb5a4a311c4008441",
            ],  # WETH
            "0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0": [
                "0x6320cd32aa674d2898a68ec82e869385fc5f7e2f"
            ],  # wstETH
            "0xae78736cd615f374d3085123a210448e74fc6393": [
                "0x62bc478ffc429161115a6e4090f819ce5c50a5d9"
            ],  # rETH
        }
        underlying_addresses = models.token.objects.all().values_list(
            "underlying_address", flat=True
        )
        addresses = []
        for a in underlying_addresses:
            addresses.append(MAPPING_TO_ETHEREUM.get(a, a))
        prices_mapping = get_current_prices(addresses)
        for key, values in prices_mapping.items():
            _, underlying_address = key.split(":")
            underlying_addresses = MAPPING_TO_GOERLI.get(
                underlying_address, [underlying_address]
            )
            for underlying_address in underlying_addresses:
                price = Decimal(str(values["price"]))
                _save_price_for_address(models, underlying_address, price)

    else:
        underlying_addresses = models.token.objects.all().values_list(
            "underlying_address", flat=True
        )
        prices_mapping = get_current_prices(underlying_addresses)

        done_addresses = set()
        for key, values in prices_mapping.items():
            _, underlying_address = key.split(":")
            done_addresses.add(underlying_addresses)

            price = Decimal(str(values["price"]))
            _save_price_for_address(models, underlying_address, price)

        _handle_rhinofi_tokens(models, done_addresses)
