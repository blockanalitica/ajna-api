import hashlib
import logging
from decimal import Decimal

from ajna.utils.wad import wad_to_decimal

log = logging.getLogger(__name__)


def _generate_reserve_auction_uid(pool_address, current_burn_epoch):
    key = "{}_{}".format(pool_address, current_burn_epoch).encode("utf-8")
    return hashlib.md5(key).hexdigest()


def process_kick_reserve_auction_event(chain, event):
    try:
        chain.reserve_auction_kick.objects.get(order_index=event.order_index)
    except chain.reserve_auction_kick.DoesNotExist:
        pass
    else:
        # If reserve_auction_kick already exists, don't process it
        return

    # get kicker from transaction
    transaction_info = chain.eth.get_transaction(event.transaction_hash)
    kicker = transaction_info["from"].lower()

    claimable_reserves = wad_to_decimal(event.data["claimableReservesRemaining"])

    # kicker award = claimableReserves * 0.01
    kicker_award = claimable_reserves * Decimal("0.01")

    reserve_auction_uid = _generate_reserve_auction_uid(
        event.pool_address, event.data["currentBurnEpoch"]
    )
    kick = chain.reserve_auction_kick.objects.create(
        order_index=event.order_index,
        reserve_auction_uid=reserve_auction_uid,
        pool_address=event.pool_address,
        burn_epoch=event.data["currentBurnEpoch"],
        kicker=kicker,
        kicker_award=kicker_award,
        claimable_reserves=claimable_reserves,
        starting_price=wad_to_decimal(event.data["auctionPrice"]),
        block_number=event.block_number,
        block_datetime=event.block_datetime,
        transaction_hash=event.transaction_hash,
    )

    # Create reserve auction
    chain.reserve_auction.objects.create(
        uid=reserve_auction_uid,
        pool_address=event.pool_address,
        claimable_reserves=kick.claimable_reserves,
        claimable_reserves_remaining=kick.claimable_reserves,
        last_take_price=kick.starting_price,
        burn_epoch=kick.burn_epoch,
        ajna_burned=Decimal("0"),
    )


def process_reserve_auction_event(chain, event):
    try:
        chain.reserve_auction_take.objects.get(order_index=event.order_index)
    except chain.reserve_auction_take.DoesNotExist:
        pass
    else:
        # If reserve_auction_take already exists, don't process it
        return

    pool = chain.pool.objects.get(address=event.pool_address)

    # get taker from transaction
    transaction_info = chain.eth.get_transaction(event.transaction_hash)
    taker = transaction_info["from"].lower()

    reserve_auction_uid = _generate_reserve_auction_uid(
        event.pool_address, event.data["currentBurnEpoch"]
    )
    reserve_auction = chain.reserve_auction.objects.get(uid=reserve_auction_uid)

    burn_data_calls = [
        (
            event.pool_address,
            [
                "burnInfo(uint256)((uint256,uint256,uint256))",
                event.data["currentBurnEpoch"],
            ],
            ["burnInfo", None],
        ),
    ]

    burn_data = chain.multicall(burn_data_calls, block_identifier=event.block_number)

    total_burned = wad_to_decimal(burn_data["burnInfo"][2])

    # since only one reserve auction can occur at a time, look at the difference since
    # the last reserve auction
    ajna_burned = total_burned - pool.total_ajna_burned

    auction_price = wad_to_decimal(event.data["auctionPrice"])
    # event does not provide amount of quote purchased. Use auction price and ajna
    # burned to calculate it
    quote_purchased = ajna_burned / auction_price

    take = chain.reserve_auction_take.objects.create(
        order_index=event.order_index,
        reserve_auction_uid=reserve_auction.uid,
        pool_address=event.pool_address,
        taker=taker,
        claimable_reserves_remaining=wad_to_decimal(
            event.data["claimableReservesRemaining"]
        ),
        auction_price=auction_price,
        ajna_burned=ajna_burned,
        quote_purchased=quote_purchased,
        block_number=event.block_number,
        block_datetime=event.block_datetime,
        transaction_hash=event.transaction_hash,
    )

    # Update reserve auction
    reserve_auction.claimable_reserves_remaining = take.claimable_reserves_remaining
    reserve_auction.last_take_price = take.auction_price
    reserve_auction.ajna_burned += take.ajna_burned
    reserve_auction.save()

    # Update pool
    pool.total_ajna_burned = total_burned
    pool.save(update_fields=["total_ajna_burned"])
