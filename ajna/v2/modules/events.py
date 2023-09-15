import logging

from django.core.cache import cache
from web3 import Web3

from ajna.utils.utils import compute_order_index

log = logging.getLogger(__name__)


POOL_INFO = {}


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


def fetch_and_save_events_for_all_pools(chain):
    cache_key = "fetch_and_save_events_for_all_pools.last_block_number"

    pool_addresses = list(chain.pool.objects.all().values_list("address", flat=True))

    from_block = cache.get(cache_key)
    if not from_block:
        # PoolCreated event is not created by this process, so we need to exclude
        # it in oreder to get the correct last block number
        last_event = (
            chain.pool_event.objects.exclude(name="PoolCreated")
            .order_by("-block_number")
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
