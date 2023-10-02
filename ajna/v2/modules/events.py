import json
import logging
from decimal import Decimal

from django.core.cache import cache
from web3 import Web3

from ajna.utils.utils import compute_order_index
from ajna.utils.wad import wad_to_decimal

log = logging.getLogger(__name__)


POOL_INFO = {}


def parse_event_data(event):
    data = None

    event_data = None
    if event["data"]:
        event_data = json.loads(event["data"])

    match event["name"]:
        case "UpdateInterestRate":
            data = {
                "newRate": wad_to_decimal(event_data["newRate"]),
                "oldRate": wad_to_decimal(event_data["oldRate"]),
            }
        case "DrawDebt":
            data = {
                "lup": wad_to_decimal(event_data["lup"]),
                "amountBorrowed": wad_to_decimal(event_data["amountBorrowed"]),
                "borrower": event_data["borrower"],
                "collateralPledged": wad_to_decimal(event_data["collateralPledged"]),
            }
        case "RepayDebt":
            data = {
                "lup": wad_to_decimal(event_data["lup"]),
                "quoteRepaid": wad_to_decimal(event_data["quoteRepaid"]),
                "borrower": event_data["borrower"],
                "collateralPulled": wad_to_decimal(event_data["collateralPulled"]),
            }
        case "AddQuoteToken":
            data = {
                "lup": wad_to_decimal(event_data["lup"]),
                "index": event_data["index"],
                "amount": wad_to_decimal(event_data["amount"]),
                "lender": event_data["lender"],
                "lpAwarded": wad_to_decimal(event_data["lpAwarded"]),
            }
        case "RemoveQuoteToken":
            data = {
                "lup": wad_to_decimal(event_data["lup"]),
                "index": event_data["index"],
                "amount": wad_to_decimal(event_data["amount"]),
                "lender": event_data["lender"],
                "lpRedeemed": wad_to_decimal(event_data["lpRedeemed"]),
            }
        case "MoveQuoteToken":
            data = {
                "lup": wad_to_decimal(event_data["lup"]),
                "to": event_data["to"],
                "from": event_data["from"],
                "amount": wad_to_decimal(event_data["amount"]),
                "lender": event_data["lender"],
                "lpAwardedTo": wad_to_decimal(event_data["lpAwardedTo"]),
                "lpRedeemedFrom": wad_to_decimal(event_data["lpRedeemedFrom"]),
            }
        case "AddCollateral":
            data = {
                "index": event_data["index"],
                "amount": wad_to_decimal(event_data["amount"]),
                "actor": event_data["actor"],
                "lpAwarded": wad_to_decimal(event_data["lpAwarded"]),
            }
        case "RemoveCollateral":
            data = {
                "index": event_data["index"],
                "amount": wad_to_decimal(event_data["amount"]),
                "claimer": event_data["claimer"],
                "lpRedeemed": wad_to_decimal(event_data["lpRedeemed"]),
            }
        case "Kick":
            data = {
                "bond": wad_to_decimal(event_data["bond"]),
                "debt": wad_to_decimal(event_data["debt"]),
                "borrower": event_data["borrower"],
                "collateral": wad_to_decimal(event_data["collateral"]),
            }
        case "KickReserveAuction":
            data = {
                "auctionPrice": wad_to_decimal(event_data["auctionPrice"]),
                "claimableReservesRemaining": wad_to_decimal(
                    event_data["claimableReservesRemaining"]
                ),
                "currentBurnEpoch": event_data["currentBurnEpoch"],
            }
        case "Settle":
            data = {
                "borrower": event_data["borrower"],
                "settledDebt": wad_to_decimal(event_data["settledDebt"]),
            }
        case "AuctionSettle":
            data = {
                "borrower": event_data["borrower"],
                "collateral": wad_to_decimal(event_data["collateral"]),
            }
        case "Take":
            data = {
                "borrower": event_data["borrower"],
                "amount": wad_to_decimal(event_data["amount"]),
                "isReward": event_data["isReward"],
                "bondChange": wad_to_decimal(event_data["bondChange"]),
                "collateral": wad_to_decimal(event_data["collateral"]),
            }
        case "BondWithdrawn":
            data = {
                "kicker": event_data["kicker"],
                "reciever": event_data["reciever"],
                "amount": wad_to_decimal(event_data["amount"]),
            }
    return data


def _get_wallet_addresses(event):
    wallet_addresses = None
    match event["event"]:
        case "DrawDebt":
            wallet_addresses = [event["args"]["borrower"]]
        case "RepayDebt":
            wallet_addresses = [event["args"]["borrower"]]
        case "AddQuoteToken":
            wallet_addresses = [event["args"]["lender"]]
        case "RemoveQuoteToken":
            wallet_addresses = [event["args"]["lender"]]
        case "MoveQuoteToken":
            wallet_addresses = [event["args"]["lender"]]
        case "AddCollateral":
            wallet_addresses = [event["args"]["actor"]]
        case "RemoveCollateral":
            wallet_addresses = [event["args"]["claimer"]]
        case "Kick":
            wallet_addresses = [event["args"]["borrower"]]
        case "BucketTake":
            wallet_addresses = [event["args"]["borrower"]]
        case "Settle":
            wallet_addresses = [event["args"]["borrower"]]
        case "AuctionSettle":
            wallet_addresses = [event["args"]["borrower"]]
        case "Take":
            wallet_addresses = [event["args"]["borrower"]]
        case "BucketTakeLPAwarded":
            wallet_addresses = [event["args"]["taker"], event["args"]["kicker"]]
        case "ApproveLPTransferors":
            wallet_addresses = [event["args"]["lender"]]
            wallet_addresses += event["args"]["transferors"]
        case "IncreaseLPAllowance":
            wallet_addresses = [event["args"]["owner"], event["args"]["spender"]]
        case "TransferLP":
            wallet_addresses = [event["args"]["owner"], event["args"]["newOwner"]]
        case "AuctionSettle":
            wallet_addresses = [event["args"]["borrower"]]
        case "Take":
            wallet_addresses = [event["args"]["borrower"]]
        case "Settle":
            wallet_addresses = [event["args"]["borrower"]]
        case "BondWithdrawn":
            wallet_addresses = [event["args"]["kicker"], event["args"]["reciever"]]
        case "LoanStamped":
            wallet_addresses = [event["args"]["borrower"]]
        # case _:
        #     print("#TODO: wallet_addresses", event["event"])
        #     pass

    if wallet_addresses:
        wallet_addresses = [w.lower() for w in wallet_addresses]
    return wallet_addresses


def _get_token_price(chain, token_address, dt):
    try:
        price = (
            chain.price_feed.objects.filter(
                underlying_address=token_address,
                datetime__lte=dt,
            )
            .latest()
            .price
        )
    except chain.price_feed.DoesNotExist:
        price = None

    return price


def _get_pool_info(chain, pool_address):
    global POOL_INFO

    if pool_address not in POOL_INFO:
        pool = chain.pool.objects.get(address=pool_address)
        POOL_INFO[pool_address] = {
            "collateral_token_address": pool.collateral_token_address,
            "quote_token_address": pool.quote_token_address,
        }

    return POOL_INFO[pool_address]


def _create_notification(chain, event, quote_token_price, order_index):
    match event["event"]:
        case "AddQuoteToken":
            if quote_token_price:
                amount = wad_to_decimal(event["args"]["amount"])
                amount_usd = amount * quote_token_price
                if amount_usd >= Decimal("1000000"):
                    chain.notification.objects.create(
                        type=event["event"],
                        key=order_index,
                        data={
                            "amount": amount,
                            "quote_token_price": quote_token_price,
                            "amount_usd": amount_usd,
                            "lp_awarded": wad_to_decimal(event["args"]["lpAwarded"]),
                            "pool_address": event["address"].lower(),
                            "wallet_address": event["args"]["lender"].lower(),
                        },
                    )
        case "DrawDebt":
            if quote_token_price:
                amount = wad_to_decimal(event["args"]["amountBorrowed"])
                amount_usd = amount * quote_token_price
                if amount_usd >= Decimal("1000000"):
                    chain.notification.objects.create(
                        type=event["event"],
                        key=order_index,
                        data={
                            "amount": amount,
                            "quote_token_price": quote_token_price,
                            "amount_usd": amount_usd,
                            "collateral": wad_to_decimal(
                                event["args"]["collateralPledged"]
                            ),
                            "pool_address": event["address"].lower(),
                            "wallet_address": event["args"]["borrower"].lower(),
                        },
                    )


def fetch_and_save_events_for_all_pools(chain):
    cache_key = "fetch_and_save_events_for_all_pools.{}.last_block_number".format(
        chain.unique_key
    )

    pool_addresses = list(chain.pool.objects.all().values_list("address", flat=True))

    if not pool_addresses:
        log.debug("No pool addresses. Skipping fetch_and_save_events_for_all_pools")
        return

    from_block = cache.get(cache_key)
    if not from_block:
        # PoolCreated event is not created by this process, so we need to exclude
        # it in order to get the correct last block number
        last_event = (
            chain.pool_event.objects.exclude(name="PoolCreated")
            .order_by("-order_index")
            .first()
        )

        if last_event:
            from_block = last_event.block_number + 1
        else:
            from_block = chain.erc20_pool_factory_start_block

    to_block = chain.get_latest_block()

    pool_addresses = [Web3.to_checksum_address(address) for address in pool_addresses]
    events = chain.get_events_for_contracts(
        pool_addresses, from_block=from_block, to_block=to_block
    )

    pool_events = []
    for event in events:
        pool_address = event["address"].lower()
        order_index = compute_order_index(
            event["blockNumber"], event["transactionIndex"], event["logIndex"]
        )
        block_datetime = chain.get_block_datetime(event["blockNumber"])
        collateral_token_price = None
        quote_token_price = None

        match event["event"]:
            case "DrawDebt" | "RepayDebt":
                pool_info = _get_pool_info(chain, pool_address)
                collateral_token_price = _get_token_price(
                    chain, pool_info["collateral_token_address"], block_datetime
                )
                quote_token_price = _get_token_price(
                    chain, pool_info["quote_token_address"], block_datetime
                )
            case "AddQuoteToken" | "RemoveQuoteToken" | "MoveQuoteToken":
                pool_info = _get_pool_info(chain, pool_address)
                quote_token_price = _get_token_price(
                    chain, pool_info["quote_token_address"], block_datetime
                )
            case "AddCollateral" | "RemoveCollateral":
                pool_info = _get_pool_info(chain, pool_address)
                collateral_token_price = _get_token_price(
                    chain, pool_info["collateral_token_address"], block_datetime
                )

        _create_notification(chain, event, quote_token_price, order_index)

        pool_events.append(
            chain.pool_event(
                pool_address=pool_address,
                wallet_addresses=_get_wallet_addresses(event),
                block_number=event["blockNumber"],
                block_datetime=block_datetime,
                order_index=order_index,
                transaction_hash=event["transactionHash"].hex(),
                name=event["event"],
                data=dict(event["args"]),
                collateral_token_price=collateral_token_price,
                quote_token_price=quote_token_price,
            )
        )

        if len(pool_events) > 500:
            log.debug("Saving pool events chunk")
            chain.pool_event.objects.bulk_create(pool_events, ignore_conflicts=True)
            pool_events = []

    if pool_events:
        log.debug("Saving last pool events chunk")
        chain.pool_event.objects.bulk_create(pool_events, ignore_conflicts=True)

    # Set the block number up to which we've fetch the events so next run we start
    # fetching from this block number. This immensly helps with pools which are not
    # that active.
    cache.set(cache_key, to_block, timeout=None)
