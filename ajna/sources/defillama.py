from decimal import Decimal

from ajna import metrics
from ajna.utils.http import retry_get_json
from ajna.utils.utils import chunks

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

    # chunk coins into batches of 50, as otherwise we sometimes overload the defillama
    # server
    coin_chunks = chunks(coins, 50)
    prices = {}
    for coins in coin_chunks:
        response = fetch_current_price(coins)
        for coin, data in response.items():
            _, address = coin.split(":")
            if address in inv_coingecko_map:
                address = inv_coingecko_map[address]

            # They've introduced a bug in their API where they sometimes don't return
            # price and timestamp, but return everything else...
            if "price" in data:
                prices[address.lower()] = Decimal(str(data["price"]))
            else:
                metrics.increment("defillama.get_current_prices_map.{}.no_price".format(chain_name))
    return prices


def get_price_for_timestamp(timestamp, address, chain_name="ethereum"):
    coin = f"{chain_name}:{address}"
    data = fetch_price_for_timestamp(timestamp, [coin])
    return data.get(coin)
