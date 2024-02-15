import json
import logging

from django.core.cache import cache
from web3 import Web3

from ajna.utils.utils import compute_order_index
from ajna.utils.wad import wad_to_decimal

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
                "actor": event_data["actor"].lower(),
                "lpAwarded": wad_to_decimal(event_data["lpAwarded"]),
            }
        case "AddCollateralNFT":
            pass  # TODO
        case "AddQuoteToken":
            data = {
                "lup": wad_to_decimal(event_data["lup"]),
                "index": event_data["index"],
                "amount": wad_to_decimal(event_data["amount"]),
                "lender": event_data["lender"].lower(),
                "lpAwarded": wad_to_decimal(event_data["lpAwarded"]),
            }
        case "ApproveLPTransferors":
            data = {
                "lender": event_data["lender"].lower(),
                "transferors": [t.lower() for t in event_data["transferors"]],
            }
        case "AuctionNFTSettle":
            data = {
                "borrower": event_data["borrower"].lower(),
            }
        case "AuctionSettle":
            data = {
                "borrower": event_data["borrower"].lower(),
                "collateral": wad_to_decimal(event_data["collateral"]),
            }
        case "BondWithdrawn":
            data = {
                "kicker": event_data["kicker"].lower(),
                "reciever": event_data["reciever"].lower(),
                "amount": wad_to_decimal(event_data["amount"]),
            }
        case "BucketBankruptcy":
            data = {
                "index": event_data["index"],
                "lpForfeited": wad_to_decimal(event_data["lpForfeited"]),
            }
            pass
        case "BucketTake":
            data = {
                "index": event_data["index"],
                "amount": wad_to_decimal(event_data["amount"]),
                "borrower": event_data["borrower"].lower(),
                "isReward": event_data["isReward"],
                "bondChange": wad_to_decimal(event_data["bondChange"]),
                "collateral": wad_to_decimal(event_data["collateral"]),
            }

        case "BucketTakeLPAwarded":
            data = {
                "taker": event_data["taker"].lower(),
                "kicker": event_data["kicker"].lower(),
                "lpAwardedTaker": wad_to_decimal(event_data["lpAwardedTaker"]),
                "lpAwardedKicker": wad_to_decimal(event_data["lpAwardedKicker"]),
            }
        case "DecreaseLPAllowance":
            pass  # TODO
        case "DrawDebt":
            data = {
                "lup": wad_to_decimal(event_data["lup"]),
                "amountBorrowed": wad_to_decimal(event_data["amountBorrowed"]),
                "borrower": event_data["borrower"].lower(),
                "collateralPledged": wad_to_decimal(event_data["collateralPledged"]),
            }
        case "DrawDebtNFT":
            data = {
                "lup": wad_to_decimal(event_data["lup"]),
                "amountBorrowed": wad_to_decimal(event_data["amountBorrowed"]),
                "borrower": event_data["borrower"].lower(),
                "tokenIdsPledged": event_data["tokenIdsPledged"],
            }
        case "Flashloan":
            pass  # TODO
        case "IncreaseLPAllowance":
            data = {
                "indexes": event_data["indexes"],
                "amounts": [wad_to_decimal(a) for a in event_data["amounts"]],
                "owner": event_data["owner"].lower(),
                "spender": event_data["spender"].lower(),
            }
            pass
        case "Kick":
            data = {
                "bond": wad_to_decimal(event_data["bond"]),
                "debt": wad_to_decimal(event_data["debt"]),
                "borrower": event_data["borrower"].lower(),
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
            data = {
                "borrower": event_data["borrower"].lower(),
            }
            pass
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
                "borrower": event_data["borrower"].lower(),
                "collateralPulled": wad_to_decimal(event_data["collateralPulled"]),
            }
        case "ReserveAuction":
            data = {
                "auctionPrice": wad_to_decimal(event_data["auctionPrice"]),
                "claimableReservesRemaining": wad_to_decimal(
                    event_data["claimableReservesRemaining"]
                ),
                "currentBurnEpoch": event_data["currentBurnEpoch"],
            }
        case "ResetInterestRate":
            data = {
                "newRate": wad_to_decimal(event_data["newRate"]),
                "oldRate": wad_to_decimal(event_data["oldRate"]),
            }
        case "RevokeLPAllowance":
            pass  # TODO
        case "RevokeLPTransferors":
            pass  # TODO
        case "Settle":
            data = {
                "borrower": event_data["borrower"].lower(),
                "settledDebt": wad_to_decimal(event_data["settledDebt"]),
            }
        case "Take":
            data = {
                "borrower": event_data["borrower"].lower(),
                "amount": wad_to_decimal(event_data["amount"]),
                "isReward": event_data["isReward"],
                "bondChange": wad_to_decimal(event_data["bondChange"]),
                "collateral": wad_to_decimal(event_data["collateral"]),
            }
        case "TransferLP":
            data = {
                "owner": event_data["owner"].lower(),
                "newOwner": event_data["newOwner"].lower(),
                "lp": wad_to_decimal(event_data["lp"]),
                "indexes": event_data["indexes"],
            }
        case "UpdateInterestRate":
            data = {
                "newRate": wad_to_decimal(event_data["newRate"]),
                "oldRate": wad_to_decimal(event_data["oldRate"]),
            }
    return data


def _get_wallet_addresses(event):
    wallet_addresses = None
    match event["event"]:
        case "AddCollateral":
            wallet_addresses = [event["args"]["actor"]]
        case "AddCollateralNFT":
            wallet_addresses = [event["args"]["actor"]]
        case "AddQuoteToken":
            wallet_addresses = [event["args"]["lender"]]
        case "ApproveLPTransferors":
            wallet_addresses = [event["args"]["lender"]]
            wallet_addresses += event["args"]["transferors"]
        case "AuctionNFTSettle":
            wallet_addresses = [event["args"]["borrower"]]
        case "AuctionSettle":
            wallet_addresses = [event["args"]["borrower"]]
        case "BondWithdrawn":
            wallet_addresses = [event["args"]["kicker"], event["args"]["reciever"]]
        case "BucketTake":
            wallet_addresses = [event["args"]["borrower"]]
        case "BucketTakeLPAwarded":
            wallet_addresses = [event["args"]["taker"], event["args"]["kicker"]]
        case "DrawDebt":
            wallet_addresses = [event["args"]["borrower"]]
        case "DrawDebtNFT":
            wallet_addresses = [event["args"]["borrower"]]
        case "IncreaseLPAllowance":
            wallet_addresses = [event["args"]["owner"], event["args"]["spender"]]
        case "Kick":
            wallet_addresses = [event["args"]["borrower"]]
        case "LoanStamped":
            wallet_addresses = [event["args"]["borrower"]]
        case "MergeOrRemoveCollateralNFT":
            wallet_addresses = [event["args"]["actor"]]
        case "MoveQuoteToken":
            wallet_addresses = [event["args"]["lender"]]
        case "RemoveCollateral":
            wallet_addresses = [event["args"]["claimer"]]
        case "RemoveQuoteToken":
            wallet_addresses = [event["args"]["lender"]]
        case "RepayDebt":
            wallet_addresses = [event["args"]["borrower"]]
        case "Settle":
            wallet_addresses = [event["args"]["borrower"]]
        case "Take":
            wallet_addresses = [event["args"]["borrower"]]
        case "TransferLP":
            wallet_addresses = [event["args"]["owner"], event["args"]["newOwner"]]
        case (
            "BucketBankruptcy"
            | "KickReserveAuction"
            | "ReserveAuction"
            | "UpdateInterestRate"
            | "ResetInterestRate"
        ):
            # Skip these events as they don't touch any wallets
            pass
        case _:
            log.error(
                "Missing _get_wallet_addresses case for event: %s",
                event["event"],
                extra={
                    "event": event["event"],
                    "pool": event["address"].lower(),
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
            case "DrawDebt" | "RepayDebt" | "DrawDebtNFT":
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
            case "Kick" | "Take" | "BucketTake" | "Settle" | "AuctionSettle":
                pool_info = _get_pool_info(chain, pool_address)
                collateral_token_price = _get_token_price(
                    chain, pool_info["collateral_token_address"], block_datetime
                )
                quote_token_price = _get_token_price(
                    chain, pool_info["quote_token_address"], block_datetime
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
    cache.set(cache_key, to_block + 1, timeout=None)
