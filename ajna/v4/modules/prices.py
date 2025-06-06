import logging
from datetime import datetime
from decimal import Decimal

from ajna.constants import MAX_PRICE_DECIMAL
from ajna.sources.defillama import get_current_prices_map
from ajna.sources.rhinofi import fetch_pair_price
from ajna.utils.db import fetch_one

log = logging.getLogger(__name__)

STABLECOIN_SYMBOLS = {
    "USDT",
    "USDC",
    "USDe",
    "DAI",
    "FDUSD",
    "USDD",
    "TUSD",
    "PYUSD",
    "USD0",
    "FRAX",
    "USDY",
    "USDJ",
    "EURS",
    "USTC",
    "USDB",
    "USDP",
    "EURC",
    "USDX",
    "BUSD",
    "LUSD",
    "GUSD",
    "vBUSD",
    "AEUR",
    "USDL",
    "SBD",
    "XSGD",
    "EURt",
    "ERUI",
    "CUSD",
    "USDG",
    "RSV",
    "ZUSD",
    "IDRT",
    "USDV",
    "EDLC",
    "SUSD",
    "GYEN",
    "MNEE",
    "BIDR",
    "HUSD",
    "VCHF",
    "FEI",
    "vDAI",
    "OUSD",
    "CEUR",
    "VEUR",
    "VAI",
    "MKUSD",
    "DJED",
    "USDs",
    "ESD",
    "IDRX",
    "BAC",
    "USDS",
    "savUSD",
    "USDC.e",
}

RHINOFI_MAP = {
    "0x0274a704a6d9129f90a62ddc6f6024b33ecdad36": {
        "rhino_pair": "YIELDBTC:BTC",
        "price_token": "WBTC",
    }
}

HEMI_FORCE_MAP = {
    # msBTC 1:1 with WBTC
    "msBTC": {"network": "ethereum", "address": "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599"}
}

DEFILLAMA_CHAIN_MAP = {"avalanche": "avax"}

# Note: make sure the address is lowercase
COINGECKO_MAP = {
    "0x10398abc267496e49106b07dd6be13364d10dc71": "let-s-get-hai",
    "0x20fe91f17ec9080e3cac2d688b4ecb48c5ac3a9c": "yes-money",
}


def _save_price_for_address(models, address, price, is_estimated_price=False):
    models.token.objects.filter(underlying_address=address).update(
        underlying_price=price, is_estimated_price=is_estimated_price
    )
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
            estimated=is_estimated_price,
        )


def _get_rhiofi_price(models, address):
    data = RHINOFI_MAP[address]
    price_token = models.token.objects.get(symbol=data["price_token"])
    conversion_price = fetch_pair_price(data["rhino_pair"])
    return price_token.underlying_price * conversion_price


def _estimate_price_from_pools_for_token(models, address, symbol):
    # When estimating, if it's a stablecoin, set it to $1
    if symbol in STABLECOIN_SYMBOLS:
        return Decimal("1")

    sql = f"""
        SELECT
            MIN(x.price) AS price
        FROM (
            SELECT
                p.hpb * qt.underlying_price AS price
            FROM {models.pool._meta.db_table} AS p
            JOIN {models.token._meta.db_table} AS qt
                ON p.quote_token_address = qt.underlying_address
            WHERE p.collateral_token_address = %s AND p.hpb < %s
        ) x
    """

    sql_vars = [address, MAX_PRICE_DECIMAL]
    data = fetch_one(sql, sql_vars)
    return data["price"]


def update_token_prices(models, network):
    """
    Updates the underlying_price field for all Token instances in the database.

    This function retrieves all the underlying addresses of the tokens, fetches the
    current prices for those addresses, and then updates the corresponding token
    instances with the new prices."""
    tokens = models.token.objects.all().values_list("underlying_address", "symbol")
    if not tokens:
        return

    underlying_addresses = [token[0] for token in tokens]

    chain_name = DEFILLAMA_CHAIN_MAP.get(network, network)
    price_mapping = get_current_prices_map(
        underlying_addresses, chain_name=chain_name, coingecko_map=COINGECKO_MAP
    )
    for address, symbol in tokens:
        if address in price_mapping:
            _save_price_for_address(models, address, price_mapping[address])
        else:
            # Catch all and any exceptions so that defillama prices are saved even
            # if any other price fetching/calculation fails.
            is_estimated_price = False
            try:
                if address in RHINOFI_MAP:
                    price = _get_rhiofi_price(models, address)
                elif network == "hemi" and symbol in HEMI_FORCE_MAP:
                    coin = HEMI_FORCE_MAP[symbol]
                    hemi_price_map = get_current_prices_map([coin["address"]], coin["network"], {})
                    price = hemi_price_map.get(coin["address"])
                else:
                    price = _estimate_price_from_pools_for_token(models, address, symbol)
                    is_estimated_price = True

                if price is not None:
                    _save_price_for_address(models, address, price, is_estimated_price)
            except Exception:
                log.exception("Couldn't fetch price for %s", address)
