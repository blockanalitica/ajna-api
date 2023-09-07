import logging
from datetime import datetime

from chain_harvester.constants import MULTICALL_ADDRESSES
from django.core.cache import cache
from web3 import Web3

from ajna.utils.utils import compute_order_index
from ajna.utils.wad import wad_to_decimal

log = logging.getLogger(__name__)


def _fetch_pool_block_data(chain, pool_address, block_number):
    global POOL_BLOCK_DATA
    inflator_info_calls = [
        (
            pool_address,
            ["inflatorInfo()((uint256,uint256))"],
            ["inflatorInfo", None],
        ),
        (
            MULTICALL_ADDRESSES[chain.chain_id],
            ["getCurrentBlockTimestamp()(uint256)"],
            ["block_timestamp", None],
        ),
    ]
    data = chain.multicall(inflator_info_calls, block_identifier=block_number)
    return {
        "inflator": wad_to_decimal(data["inflatorInfo"][0]),
        "block_datetime": datetime.fromtimestamp(data["block_timestamp"]),
    }


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
        # case _:
        #     print("#TODO: wallet_addresses", event["event"])
        #     pass

    if wallet_addresses:
        wallet_addresses = [w.lower() for w in wallet_addresses]
    return wallet_addresses


def fetch_and_save_events_for_pool(chain, pool_address, from_block=None):
    cache_key = "fetch_and_save_events_for_pool.{}.last_block_number".format(
        pool_address
    )

    if not from_block:
        from_block = cache.get(cache_key)
        if not from_block:
            last_event = (
                chain.pool_event.objects.filter(pool_address=pool_address)
                .order_by("-block_number")
                .first()
            )

            if last_event:
                from_block = last_event.block_number + 1
            else:
                pool = chain.pool.objects.get(address=pool_address)
                from_block = pool.created_at_block_number

    to_block = chain.get_latest_block()

    events = chain.get_events_for_contract(
        Web3.to_checksum_address(pool_address), from_block=from_block, to_block=to_block
    )

    blocks_data = {}
    pool_events = []
    for event in events:
        block_data = blocks_data.get(event["blockNumber"])
        if not block_data:
            block_data = _fetch_pool_block_data(
                chain, pool_address, event["blockNumber"]
            )
            blocks_data[event["blockNumber"]] = block_data

        pool_events.append(
            chain.pool_event(
                pool_address=pool_address.lower(),
                wallet_addresses=_get_wallet_addresses(event),
                block_number=event["blockNumber"],
                block_datetime=block_data["block_datetime"],
                order_index=compute_order_index(
                    event["blockNumber"], event["transactionIndex"], event["logIndex"]
                ),
                transaction_hash=event["transactionHash"].hex(),
                name=event["event"],
                data=dict(event["args"]),
                pool_inflator=block_data["inflator"],
            )
        )

        if len(pool_events) > 500:
            chain.pool_event.objects.bulk_create(pool_events, ignore_conflicts=True)
            pool_events = []

    if pool_events:
        chain.pool_event.objects.bulk_create(pool_events, ignore_conflicts=True)

    # Set the block number up to which we've fetch the events so next run we start
    # fetching from this block number. This immensly helps with pools which are not
    # that active.
    cache.set(cache_key, to_block, timeout=None)
