from datetime import datetime
from decimal import Decimal

from web3 import Web3


def _get_wallet_address(chain, address):
    address = Web3.toChecksumAddress(address)
    code = chain.eth.get_code(address).hex()
    if len(code) > 2:
        address = chain.get_eoa(address)
    return address.lower()


def fetch_and_save_settled_liquidation_auctions(
    chain, subgraph, liquidation_auction_model, price_feed_model, settle_time=0
):
    """
    Fetches liquidationAuctions from the Subgraph and saves it to the LiquidationAuctions
    model.
    """
    auctions = subgraph.settled_liquidation_auctions(settle_time)
    for auction in auctions:
        collateral_token_address = auction["pool"]["collateralToken"]["id"]
        debt_token_address = auction["pool"]["quoteToken"]["id"]
        dt = datetime.fromtimestamp(int(auction["settleTime"]))
        try:
            collateral_underlying_price = (
                price_feed_model.objects.filter(
                    underlying_address=collateral_token_address, datetime__lte=dt
                )
                .latest()
                .price
            )
        except price_feed_model.DoesNotExist:
            try:
                collateral_underlying_price = (
                    price_feed_model.objects.filter(
                        underlying_address=collateral_token_address
                    )
                    .earliest()
                    .price
                )
            except price_feed_model.DoesNotExist:
                collateral_underlying_price = None
        try:
            debt_underlying_price = (
                price_feed_model.objects.filter(
                    underlying_address=debt_token_address, datetime__lte=dt
                )
                .latest()
                .price
            )
        except price_feed_model.DoesNotExist:
            try:
                debt_underlying_price = (
                    price_feed_model.objects.filter(underlying_address=debt_token_address)
                    .earliest()
                    .price
                )
            except price_feed_model.DoesNotExist:
                debt_underlying_price = None

        wallet_address = _get_wallet_address(chain, auction["borrower"])

        liquidation_auction_model.objects.update_or_create(
            uid=auction["id"],
            defaults={
                "settled": auction["settled"],
                "settle_time": int(auction["settleTime"]),
                "datetime": datetime.fromtimestamp(int(auction["settleTime"])),
                "neutral_price": Decimal(auction["neutralPrice"]),
                "kicker": auction["kicker"],
                "kick_time": int(auction["kickTime"]),
                "debt": Decimal(auction["debt"]),
                "collateral_remaining": Decimal(auction["collateralRemaining"]),
                "collateral": Decimal(auction["collateral"]),
                "borrower": auction["borrower"],
                "wallet_address": wallet_address,
                "bond_size": Decimal(auction["bondSize"]),
                "bond_factor": Decimal(auction["bondFactor"]),
                "last_take_price": Decimal(auction["lastTakePrice"]),
                "debt_remaining": Decimal(auction["debtRemaining"]),
                "pool_address": auction["pool"]["id"],
                "collateral_underlying_price": collateral_underlying_price,
                "debt_underlying_price": debt_underlying_price,
                "collateral_token_address": collateral_token_address,
                "debt_token_address": debt_token_address,
            },
        )


def fetch_and_save_active_liquidation_auctions(
    chain, subgraph, liquidation_auction_model
):
    """
    Fetches liquidationAuctions from the Subgraph and saves it to the LiquidationAuctions
    model.
    """
    auctions = subgraph.active_liquidation_auctions()
    for auction in auctions:
        collateral_token_address = auction["pool"]["collateralToken"]["id"]
        debt_token_address = auction["pool"]["quoteToken"]["id"]
        wallet_address = _get_wallet_address(chain, auction["borrower"])
        liquidation_auction_model.objects.update_or_create(
            uid=auction["id"],
            defaults={
                "settled": auction["settled"],
                "settle_time": auction["settleTime"],
                "datetime": datetime.now(),
                "neutral_price": Decimal(auction["neutralPrice"]),
                "kicker": auction["kicker"],
                "kick_time": int(auction["kickTime"]),
                "debt": Decimal(auction["debt"]),
                "collateral_remaining": Decimal(auction["collateralRemaining"]),
                "collateral": Decimal(auction["collateral"]),
                "borrower": auction["borrower"],
                "wallet_address": wallet_address,
                "bond_size": Decimal(auction["bondSize"]),
                "bond_factor": Decimal(auction["bondFactor"]),
                "last_take_price": Decimal(auction["lastTakePrice"]),
                "debt_remaining": Decimal(auction["debtRemaining"]),
                "pool_address": auction["pool"]["id"],
                "collateral_token_address": collateral_token_address,
                "debt_token_address": debt_token_address,
            },
        )
