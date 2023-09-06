from decimal import Decimal

import requests


def fetch_pair_price(pair):
    url = "https://api.rhino.fi/market-data/ticker/{}".format(pair)
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return Decimal(str(data[6]))
