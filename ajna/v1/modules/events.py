import logging
from datetime import datetime
from decimal import Decimal
from django.core.cache import cache

from web3 import Web3
from ajna.sources.defillama import get_price_for_timestamp
from ajna.utils.utils import compute_order_index


log = logging.getLogger(__name__)


def fetch_and_save_events_for_pool(chain, pool_address, from_block=None):
    cache_key = "fetch_and_save_events_for_pool.{}.last_block_number".format(
        pool_address
    )

    if not from_block:
        # from_block = cache.get(cache_key)
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

    pool_events = []
    cnt = 0
    for event in events:
        cnt += 1
        pool_events.append(
            chain.pool_event(
                pool_address=pool_address.lower(),
                block_number=event["blockNumber"],
                block_datetime=chain.get_block_datetime(event["blockNumber"]),
                order_index=compute_order_index(
                    event["blockNumber"], event["transactionIndex"], event["logIndex"]
                ),
                transaction_hash=event["transactionHash"].hex(),
                name=event["event"],
                data=dict(event["args"]),
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


def _get_price(price_feed_model, underlying_address, timestamp):
    if not isinstance(timestamp, int):
        timestamp = int(timestamp)

    try:
        price = (
            price_feed_model.objects.filter(
                underlying_address=underlying_address,
                timestamp__lte=timestamp,
            )
            .latest()
            .price
        )
    except price_feed_model.DoesNotExist:
        log.info(
            "Price for {} on {} doesn't exist. Fetching price.".format(
                underlying_address, timestamp
            )
        )
        price_value = get_price_for_timestamp(timestamp, underlying_address)
        if price_value:
            price = Decimal(str(price_value["price"]))
            price_feed_model.objects.get_or_create(
                underlying_address=underlying_address,
                price=price,
                datetime=datetime.fromtimestamp(timestamp),
                timestamp=timestamp,
            )
        else:
            log.info(
                "Couldn't fetch price for token {} on {}".format(
                    underlying_address, timestamp
                )
            )
            price = None

    return price


def fetch_and_save_add_collaterals(
    subgraph, add_collateral_model, price_feed_model, from_block_number
):
    """
    Fetches addCollateral events from the Subgraph and saves it to the AddCollateral
    model.
    """
    add_collaterals = subgraph.add_collaterals(from_block_number)
    for add_collateral in add_collaterals:
        underlying_address = add_collateral["pool"]["collateralToken"]["id"]
        timestamp = add_collateral["blockTimestamp"]
        price = _get_price(price_feed_model, underlying_address, timestamp)
        add_collateral_model.objects.create(
            pool_address=add_collateral["pool"]["id"],
            bucket_index=add_collateral["bucket"]["bucketIndex"],
            actor=add_collateral["actor"],
            transaction_hash=add_collateral["transactionHash"],
            index=add_collateral["index"],
            amount=add_collateral["amount"],
            lp_awarded=add_collateral["lpAwarded"],
            block_number=add_collateral["blockNumber"],
            block_timestamp=add_collateral["blockTimestamp"],
            price=price,
        )


def fetch_and_save_remove_collaterals(
    subgraph, remove_collateral_model, price_feed_model, from_block_number
):
    """
    Fetches removeCollateral events from the Subgraph and saves it to the RemoveCollateral
    model.
    """
    remove_collaterals = subgraph.remove_collaterals(from_block_number)
    for remove_collateral in remove_collaterals:
        underlying_address = remove_collateral["pool"]["collateralToken"]["id"]
        timestamp = remove_collateral["blockTimestamp"]
        price = _get_price(price_feed_model, underlying_address, timestamp)
        remove_collateral_model.objects.create(
            pool_address=remove_collateral["pool"]["id"],
            bucket_index=remove_collateral["bucket"]["bucketIndex"],
            claimer=remove_collateral["claimer"],
            transaction_hash=remove_collateral["transactionHash"],
            index=remove_collateral["index"],
            amount=remove_collateral["amount"],
            lp_redeemed=remove_collateral["lpRedeemed"],
            block_number=remove_collateral["blockNumber"],
            block_timestamp=remove_collateral["blockTimestamp"],
            price=price,
        )


def fetch_and_save_add_quote_tokens(
    subgraph, add_quote_tokens_model, price_feed_model, from_block_number
):
    """
    Fetches addQuoteToken events from the Subgraph and saves it to the AddQuoteToken
    model.
    """
    add_quote_tokens = subgraph.add_quote_tokens(from_block_number)
    for add_quote_token in add_quote_tokens:
        underlying_address = add_quote_token["pool"]["quoteToken"]["id"]
        timestamp = add_quote_token["blockTimestamp"]
        price = _get_price(price_feed_model, underlying_address, timestamp)
        lup = Decimal(add_quote_token["lup"])
        amount = Decimal(add_quote_token["amount"])
        bucket_price = Decimal(add_quote_token["bucket"]["bucketPrice"])
        deposit_fee_rate = Decimal(add_quote_token["pool"]["depositFeeRate"])
        fee = 0
        if Decimal(bucket_price) < Decimal(lup):
            fee = Decimal(amount) * Decimal((1 + deposit_fee_rate)) - Decimal(amount)

        add_quote_tokens_model.objects.create(
            pool_address=add_quote_token["pool"]["id"],
            bucket_index=add_quote_token["bucket"]["bucketIndex"],
            bucket_price=bucket_price,
            lender=add_quote_token["lender"],
            transaction_hash=add_quote_token["transactionHash"],
            index=add_quote_token["index"],
            amount=add_quote_token["amount"],
            lp_awarded=add_quote_token["lpAwarded"],
            lup=add_quote_token["lup"],
            block_number=add_quote_token["blockNumber"],
            block_timestamp=add_quote_token["blockTimestamp"],
            price=price,
            fee=fee,
            deposit_fee_rate=deposit_fee_rate,
        )


def fetch_and_save_remove_quote_tokens(
    subgraph, remove_quote_tokens_model, price_feed_model, from_block_number
):
    """
    Fetches removeQuoteToken events from the Subgraph and saves it to the RemoveQuoteToken
    model.
    """
    remove_quote_tokens = subgraph.remove_quote_tokens(from_block_number)
    for remove_quote_token in remove_quote_tokens:
        underlying_address = remove_quote_token["pool"]["quoteToken"]["id"]
        timestamp = remove_quote_token["blockTimestamp"]
        price = _get_price(price_feed_model, underlying_address, timestamp)
        remove_quote_tokens_model.objects.create(
            pool_address=remove_quote_token["pool"]["id"],
            bucket_index=remove_quote_token["bucket"]["bucketIndex"],
            lender=remove_quote_token["lender"],
            transaction_hash=remove_quote_token["transactionHash"],
            index=remove_quote_token["index"],
            amount=remove_quote_token["amount"],
            lp_redeemed=remove_quote_token["lpRedeemed"],
            lup=remove_quote_token["lup"],
            block_number=remove_quote_token["blockNumber"],
            block_timestamp=remove_quote_token["blockTimestamp"],
            price=price,
        )


def fetch_and_save_move_quote_tokens(
    subgraph, move_quote_tokens_model, price_feed_model, from_block_number
):
    """
    Fetches moveQuoteToken events from the Subgraph and saves it to the MoveQuoteToken
    model.
    """
    move_quote_tokens = subgraph.move_quote_tokens(from_block_number)
    for move_quote_token in move_quote_tokens:
        underlying_address = move_quote_token["pool"]["quoteToken"]["id"]
        timestamp = move_quote_token["blockTimestamp"]
        price = _get_price(price_feed_model, underlying_address, timestamp)
        move_quote_tokens_model.objects.create(
            pool_address=move_quote_token["pool"]["id"],
            bucket_index_from=move_quote_token["from"]["bucketIndex"],
            bucket_index_to=move_quote_token["to"]["bucketIndex"],
            lender=move_quote_token["lender"],
            transaction_hash=move_quote_token["transactionHash"],
            amount=move_quote_token["amount"],
            lp_redeemed_from=move_quote_token["lpRedeemedFrom"],
            lp_awarded_to=move_quote_token["lpAwardedTo"],
            lup=move_quote_token["lup"],
            block_number=move_quote_token["blockNumber"],
            block_timestamp=move_quote_token["blockTimestamp"],
            price=price,
        )


def fetch_and_save_draw_debts(
    subgraph, draw_debt_model, price_feed_model, from_block_number
):
    """
    Fetches drawDebt events from the Subgraph and saves it to the DrawDebt model.
    """
    draw_debts = subgraph.draw_debts(from_block_number)
    for draw_debt in draw_debts:
        collateral_underlying_address = draw_debt["pool"]["collateralToken"]["id"]
        timestamp = draw_debt["blockTimestamp"]
        collateral_price = _get_price(
            price_feed_model, collateral_underlying_address, timestamp
        )

        quote_underlying_address = draw_debt["pool"]["quoteToken"]["id"]
        timestamp = draw_debt["blockTimestamp"]

        quote_price = _get_price(price_feed_model, quote_underlying_address, timestamp)
        amount = Decimal(draw_debt["amountBorrowed"])
        borrow_fee_rate = Decimal(draw_debt["pool"]["borrowFeeRate"])
        fee = amount * Decimal((1 + borrow_fee_rate)) - amount
        draw_debt_model.objects.create(
            index=draw_debt["id"],
            pool_address=draw_debt["pool"]["id"],
            borrower=draw_debt["borrower"],
            amount_borrowed=draw_debt["amountBorrowed"],
            collateral_pledged=draw_debt["collateralPledged"],
            lup=draw_debt["lup"],
            block_number=draw_debt["blockNumber"],
            block_timestamp=draw_debt["blockTimestamp"],
            transaction_hash=draw_debt["transactionHash"],
            collateral_token_price=collateral_price,
            quote_token_price=quote_price,
            fee=fee,
            borrow_fee_rate=borrow_fee_rate,
        )


def fetch_and_save_repay_debts(
    subgraph, repay_debt_model, price_feed_model, from_block_number
):
    """
    Fetches repayDebt events from the Subgraph and saves it to the RepayDebt model.
    """
    repay_debts = subgraph.repay_debts(from_block_number)
    for repay_debt in repay_debts:
        collateral_underlying_address = repay_debt["pool"]["collateralToken"]["id"]
        timestamp = repay_debt["blockTimestamp"]

        collateral_price = _get_price(
            price_feed_model, collateral_underlying_address, timestamp
        )
        quote_underlying_address = repay_debt["pool"]["quoteToken"]["id"]
        timestamp = repay_debt["blockTimestamp"]
        quote_price = _get_price(price_feed_model, quote_underlying_address, timestamp)
        repay_debt_model.objects.create(
            index=repay_debt["id"],
            pool_address=repay_debt["pool"]["id"],
            borrower=repay_debt["borrower"],
            quote_repaid=repay_debt["quoteRepaid"],
            collateral_pulled=repay_debt["collateralPulled"],
            lup=repay_debt["lup"],
            block_number=repay_debt["blockNumber"],
            block_timestamp=repay_debt["blockTimestamp"],
            transaction_hash=repay_debt["transactionHash"],
            collateral_token_price=collateral_price,
            quote_token_price=quote_price,
        )
