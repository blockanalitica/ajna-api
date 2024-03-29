from decimal import Decimal

from ajna.utils.http import retry_get_json

LLAMA_COINS_API_URL = "https://coins.llama.fi/"


def fetch_current_price(coins):
    url = "prices/current/{}/".format(",".join(coins))
    data = retry_get_json("{}{}".format(LLAMA_COINS_API_URL, url))
    return data["coins"]


def fetch_price_for_timestamp(timestamp, coins):
    url = "prices/historical/{}/{}/".format(timestamp, ",".join(coins))
    data = retry_get_json("{}{}".format(LLAMA_COINS_API_URL, url))
    return data["coins"]


def get_current_prices(addresses, chain_name="ethereum"):
    coins = [f"{chain_name}:{address}" for address in addresses]
    data = fetch_current_price(coins)
    return data


def get_current_prices_map(addresses, chain_name, coingecko_map):
    inv_coingecko_map = {v: k for k, v in coingecko_map.items()}

    coins = []
    for address in addresses:
        if address.lower() in coingecko_map:
            coin = f"coingecko:{coingecko_map[address]}"
        else:
            coin = f"{chain_name}:{address}"

        coins.append(coin)

    response = fetch_current_price(coins)
    prices = {}
    for coin, data in response.items():
        _, address = coin.split(":")
        if address in inv_coingecko_map:  # noqa: SIM908
            address = inv_coingecko_map[address]

        prices[address.lower()] = Decimal(str(data["price"]))
    return prices


def get_price_for_timestamp(timestamp, address, chain_name="ethereum"):
    coin = f"{chain_name}:{address}"
    data = fetch_price_for_timestamp(timestamp, [coin])
    return data.get(coin)
