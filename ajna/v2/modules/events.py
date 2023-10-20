import json
import logging
from decimal import Decimal

from django.core.cache import cache
from web3 import Web3

from ajna.constants import ERC721
from ajna.utils.utils import compute_order_index
from ajna.utils.wad import wad_to_decimal
from ajna.v2.modules.auctions import (
    process_auction_settle_event,
    process_bucket_take_event,
    process_kick_event,
    process_settle_event,
    process_take_event,
)

log = logging.getLogger(__name__)


POOL_INFO = {}


def parse_event_data(event):
    data = None

    event_data = event["data"]
    if event_data and not isinstance(event_data, dict):
        event_data = json.loads(event["data"])

    match event["name"]:
        case "AddCollateral":
            data = {
                "index": event_data["index"],
                "amount": wad_to_decimal(event_data["amount"]),
                "actor": event_data["actor"],
                "lpAwarded": wad_to_decimal(event_data["lpAwarded"]),
            }
        case "AddCollateralNFT":
            pass  # TODO
        case "AddQuoteToken":
            data = {
                "lup": wad_to_decimal(event_data["lup"]),
                "index": event_data["index"],
                "amount": wad_to_decimal(event_data["amount"]),
                "lender": event_data["lender"],
                "lpAwarded": wad_to_decimal(event_data["lpAwarded"]),
            }
        case "ApproveLPTransferors":
            pass  # TODO
        case "AuctionNFTSettle":
            data = {
                "borrower": event_data["borrower"],
                "collateral": wad_to_decimal(event_data["collateral"]),
            }
        case "AuctionSettle":
            data = {
                "borrower": event_data["borrower"],
                "collateral": wad_to_decimal(event_data["collateral"]),
            }
        case "BondWithdrawn":
            data = {
                "kicker": event_data["kicker"],
                "reciever": event_data["reciever"],
                "amount": wad_to_decimal(event_data["amount"]),
            }
        case "BucketBankruptcy":
            pass  # TODO
        case "BucketTake":
            pass  # TODO
        case "BucketTakeLPAwarded":
            pass  # TODO
        case "DecreaseLPAllowance":
            pass  # TODO
        case "DrawDebt":
            data = {
                "lup": wad_to_decimal(event_data["lup"]),
                "amountBorrowed": wad_to_decimal(event_data["amountBorrowed"]),
                "borrower": event_data["borrower"],
                "collateralPledged": wad_to_decimal(event_data["collateralPledged"]),
            }
        case "DrawDebtNFT":
            data = {
                "lup": wad_to_decimal(event_data["lup"]),
                "amountBorrowed": wad_to_decimal(event_data["amountBorrowed"]),
                "borrower": event_data["borrower"],
                "tokenIdsPledged": event_data["tokenIdsPledged"],
            }
        case "Flashloan":
            pass  # TODO
        case "IncreaseLPAllowance":
            pass  # TODO
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
        case "LoanStamped":
            pass  # TODO
        case "MergeOrRemoveCollateralNFT":
            pass  # TODO
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
        case "RemoveCollateral":
            data = {
                "index": event_data["index"],
                "amount": wad_to_decimal(event_data["amount"]),
                "claimer": event_data["claimer"],
                "lpRedeemed": wad_to_decimal(event_data["lpRedeemed"]),
            }
        case "RemoveQuoteToken":
            data = {
                "lup": wad_to_decimal(event_data["lup"]),
                "index": event_data["index"],
                "amount": wad_to_decimal(event_data["amount"]),
                "lender": event_data["lender"],
                "lpRedeemed": wad_to_decimal(event_data["lpRedeemed"]),
            }
        case "RepayDebt":
            data = {
                "lup": wad_to_decimal(event_data["lup"]),
                "quoteRepaid": wad_to_decimal(event_data["quoteRepaid"]),
                "borrower": event_data["borrower"],
                "collateralPulled": wad_to_decimal(event_data["collateralPulled"]),
            }
        case "ReserveAuction":
            pass  # TODO
        case "ResetInterestRate":
            pass  # TODO
        case "RevokeLPAllowance":
            pass  # TODO
        case "RevokeLPTransferors":
            pass  # TODO
        case "Settle":
            data = {
                "borrower": event_data["borrower"],
                "settledDebt": wad_to_decimal(event_data["settledDebt"]),
            }

        case "Take":
            data = {
                "borrower": event_data["borrower"],
                "amount": wad_to_decimal(event_data["amount"]),
                "isReward": event_data["isReward"],
                "bondChange": wad_to_decimal(event_data["bondChange"]),
                "collateral": wad_to_decimal(event_data["collateral"]),
            }
        case "TransferLP":
            pass  # TODO
        case "UpdateInterestRate":
            data = {
                "newRate": wad_to_decimal(event_data["newRate"]),
                "oldRate": wad_to_decimal(event_data["oldRate"]),
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
        case "AddCollateralNFT":
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
        case "AuctionNFTSettle":
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
        case "DrawDebtNFT":
            wallet_addresses = [event["args"]["borrower"]]
        case "MergeOrRemoveCollateralNFT":
            wallet_addresses = [event["args"]["actor"]]
        case (
            "UpdateInterestRate"
            | "KickReserveAuction"
            | "ReserveAuction"
            | "BucketBankruptcy"
        ):
            # Skip these events as they don't touch any wallets
            pass
        case _:
            log.error(
                "Missing _get_wallet_addresses case for event: %s",
                event["event"],
                extra={
                    "event": event["event"],
                    "pool": event["address"],
                    "block": event["blockNumber"],
                },
            )

    if wallet_addresses:
        wallet_addresses = [w.lower() for w in wallet_addresses]
    return wallet_addresses


def _get_bucket_indexes(event):
    bucket_indexes = None
    match event["event"]:
        case "AddQuoteToken":
            bucket_indexes = [event["args"]["index"]]
        case "RemoveQuoteToken":
            bucket_indexes = [event["args"]["index"]]
        case "MoveQuoteToken":
            bucket_indexes = [event["args"]["from"], event["args"]["to"]]
        case "AddCollateral":
            bucket_indexes = [event["args"]["index"]]
        case "AddCollateralNFT":
            bucket_indexes = [event["args"]["index"]]
        case "RemoveCollateral":
            bucket_indexes = [event["args"]["index"]]
        case "BucketTake":
            bucket_indexes = [event["args"]["index"]]
        case "IncreaseLPAllowance":
            bucket_indexes = event["args"]["indexes"]
        case "TransferLP":
            bucket_indexes = event["args"]["indexes"]
        case "BucketBankruptcy":
            bucket_indexes = [event["args"]["index"]]
        case (
            "DrawDebt"
            | "RepayDebt"
            | "UpdateInterestRate"
            | "Kick"
            | "AuctionSettle"
            | "BondWithdrawn"
            | "Take"
            | "Settle"
            | "LoanStamped"
            | "KickReserveAuction"
            | "BucketTakeLPAwarded"
            | "ReserveAuction"
            | "ApproveLPTransferors"
            | "DrawDebtNFT"
            | "AuctionNFTSettle"
            | "MergeOrRemoveCollateralNFT"
        ):
            # Skip these events as they don't touch any buckets
            pass
        case _:
            log.error(
                "Missing _get_bucket_indexes case for event: %s",
                event["event"],
                extra={
                    "event": event["event"],
                    "pool": event["address"],
                    "block": event["blockNumber"],
                },
            )

    return bucket_indexes


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


def _create_notification(chain, event):
    match event.name:
        case "AddQuoteToken":
            if event.quote_token_price:
                amount = wad_to_decimal(event.data["amount"])
                amount_usd = amount * event.quote_token_price
                if amount_usd >= Decimal("1000000"):
                    chain.notification.objects.create(
                        type=event.name,
                        key=event.order_index,
                        data={
                            "amount": amount,
                            "quote_token_price": event.quote_token_price,
                            "amount_usd": amount_usd,
                            "lp_awarded": wad_to_decimal(event.data["lpAwarded"]),
                            "wallet_address": event.data["lender"].lower(),
                        },
                        datetime=event.block_datetime,
                        pool_address=event.pool_address,
                    )
        case "DrawDebt":
            if event.quote_token_price:
                amount = wad_to_decimal(event.data["amountBorrowed"])
                amount_usd = amount * event.quote_token_price
                if amount_usd >= Decimal("1000000"):
                    chain.notification.objects.create(
                        type=event.name,
                        key=event.order_index,
                        data={
                            "amount": amount,
                            "quote_token_price": event.quote_token_price,
                            "amount_usd": amount_usd,
                            "collateral": wad_to_decimal(
                                event.data["collateralPledged"]
                            ),
                            "wallet_address": event.data["borrower"].lower(),
                        },
                        datetime=event.block_datetime,
                        pool_address=event.pool_address,
                    )


def _process_auctions(chain, event):
    match event.name:
        case "Kick":
            process_kick_event(chain, event)
        case "Take":
            process_take_event(chain, event)
        case "BucketTake":
            process_bucket_take_event(chain, event)
        case "Settle":
            process_settle_event(chain, event)
        case "AuctionSettle":
            process_auction_settle_event(chain, event)


def fetch_and_save_events_for_all_pools(chain):
    cache_key = "fetch_and_save_events_for_all_pools.{}.last_block_number".format(
        chain.unique_key
    )

    # pool_addresses = list(chain.pool.objects.all().values_list("address", flat=True))
    pool_addresses = list(
        chain.pool.objects.filter(erc=ERC721).values_list("address", flat=True)
    )

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
            from_block = min(
                chain.erc20_pool_factory_start_block,
                chain.erc721_pool_factory_start_block,
            )

    from_block = min(
        chain.erc20_pool_factory_start_block,
        chain.erc721_pool_factory_start_block,
    )

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

        pool_event = chain.pool_event(
            pool_address=pool_address,
            wallet_addresses=_get_wallet_addresses(event),
            bucket_indexes=_get_bucket_indexes(event),
            block_number=event["blockNumber"],
            block_datetime=block_datetime,
            order_index=order_index,
            transaction_hash=event["transactionHash"].hex(),
            name=event["event"],
            data=dict(event["args"]),
            collateral_token_price=collateral_token_price,
            quote_token_price=quote_token_price,
        )
        pool_events.append(pool_event)
        _create_notification(chain, pool_event)

        _process_auctions(chain, pool_event)

        if len(pool_events) > 100:
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
