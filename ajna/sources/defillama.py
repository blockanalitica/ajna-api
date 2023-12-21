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


def get_price_for_timestamp(timestamp, address, chain_name="ethereum"):
    coin = f"{chain_name}:{address}"
    data = fetch_price_for_timestamp(timestamp, [coin])
    return data.get(coin)
