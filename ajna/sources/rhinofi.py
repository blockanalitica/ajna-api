from decimal import Decimal

import requests


def fetch_pair_price(pair):
    url = f"https://api.rhino.fi/market-data/ticker/{pair}"
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    data = response.json()
    return Decimal(str(data[6]))
