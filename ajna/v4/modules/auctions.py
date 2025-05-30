import hashlib
import logging
import math
from datetime import datetime
from decimal import Decimal

from ajna.utils.wad import wad_to_decimal

log = logging.getLogger(__name__)


def _generate_auction_uid(pool_address, borrower, block_number):
    key = f"{pool_address}_{borrower}_{block_number}".encode()
    return hashlib.md5(key).hexdigest()  # noqa: S324


def _create_auction(chain, pool_address, borrower, kick):
    uid = _generate_auction_uid(pool_address, borrower, kick.block_number)

    chain.auction.objects.get_or_create(
        uid=uid,
        defaults={
            "pool_address": pool_address,
            "borrower": borrower,
            "kicker": kick.kicker,
            "collateral": kick.collateral,
            "collateral_remaining": kick.collateral,
            "debt": kick.debt,
            "debt_remaining": kick.debt,
            "settled": False,
        },
    )

    _update_auction(chain, uid, kick.block_number)


def _update_auction(chain, auction_uid, block_number, last_take_price=None):
    auction = chain.auction.objects.get(uid=auction_uid)

    calls = [
        (
            auction.pool_address,
            [
                "auctionInfo(address)("
                "(address,uint256,uint256,uint256,uint256,uint256,address,"
                "address,address))",
                auction.borrower,
            ],
            ["auctionInfo", None],
        ),
        (
            chain.pool_info_address,
            [
                "auctionStatus(address,address)((uint256,uint256,uint256,bool,uint256,uint256))",
                auction.pool_address,
                auction.borrower,
            ],
            ["auctionStatus", None],
        ),
    ]

    mc_data = chain.multicall(calls, block_identifier=block_number)

    kick_time = mc_data["auctionInfo"][3]
    # kick_time of 0 indicates auction was settled and auctionInfo/auctionStatus have
    # no useful information
    if kick_time != 0:
        auction.bond_factor = wad_to_decimal(mc_data["auctionInfo"][1])
        auction.bond_size = wad_to_decimal(mc_data["auctionInfo"][2])
        auction.neutral_price = wad_to_decimal(mc_data["auctionInfo"][5])

    auction.collateral_remaining = wad_to_decimal(mc_data["auctionStatus"][1])
    auction.debt_remaining = wad_to_decimal(mc_data["auctionStatus"][2])

    if last_take_price:
        auction.last_take_price = last_take_price

    auction.save()


def _update_kick_locked_amount(chain, auction_uid, is_reward, locked_change):
    kick = (
        chain.auction_kick.objects.filter(auction_uid=auction_uid).order_by("-block_number").first()
    )
    if is_reward:
        kick.locked = kick.locked + locked_change
    else:
        kick.locked = kick.locked - locked_change
    kick.save()


def process_kick_event(chain, event):
    try:
        kick = chain.auction_kick.objects.get(order_index=event.order_index)
    except chain.auction_kick.DoesNotExist:
        pass
    else:
        # If auction_kick already exists, don't process it
        return

    borrower = event.data["borrower"].lower()
    bond = wad_to_decimal(event.data["bond"])
    current_position = chain.current_wallet_position.objects.get(
        pool_address=event.pool_address, wallet_address=borrower
    )

    # get kicker from transaction
    transaction_info = chain.eth.get_transaction(event.transaction_hash)
    kicker = transaction_info["from"].lower()

    calls = [
        (
            event.pool_address,
            [
                "auctionInfo(address)("
                "(address,uint256,uint256,uint256,uint256,uint256,address,"
                "address,address))",
                event.data["borrower"],
            ],
            ["auctionInfo", None],
        ),
        (
            chain.pool_info_address,
            [
                "auctionStatus(address,address)((uint256,uint256,uint256,bool,uint256,uint256))",
                event.pool_address,
                event.data["borrower"],
            ],
            ["auctionStatus", None],
        ),
    ]

    mc_data = chain.multicall(calls, block_identifier=event.block_number)

    reference_price = wad_to_decimal(mc_data["auctionInfo"][4])
    starting_price = wad_to_decimal(mc_data["auctionStatus"][4])

    kick = chain.auction_kick.objects.create(
        order_index=event.order_index,
        auction_uid=_generate_auction_uid(event.pool_address, borrower, event.block_number),
        pool_address=event.pool_address,
        borrower=borrower,
        debt=wad_to_decimal(event.data["debt"]),
        collateral=wad_to_decimal(event.data["collateral"]),
        bond=bond,
        locked=bond,
        block_number=event.block_number,
        block_datetime=event.block_datetime,
        transaction_hash=event.transaction_hash,
        kicker=kicker,
        reference_price=reference_price,
        starting_price=starting_price,
        collateral_token_price=event.collateral_token_price,
        quote_token_price=event.quote_token_price,
    )
    current_position.in_liquidation = True
    current_position.save()
    _create_auction(chain, event.pool_address, borrower, kick)


def process_take_event(chain, event):
    try:
        chain.auction_take.objects.get(order_index=event.order_index)
    except chain.auction_take.DoesNotExist:
        pass
    else:
        # If auction_take already exists, don't process it
        return

    borrower = event.data["borrower"].lower()

    # get taker from transaction
    transaction_info = chain.eth.get_transaction(event.transaction_hash)
    taker = transaction_info["from"].lower()

    amount = wad_to_decimal(event.data["amount"])
    collateral = wad_to_decimal(event.data["collateral"])
    bond_change = wad_to_decimal(event.data["bondChange"])

    auction = chain.auction.objects.get(
        pool_address=event.pool_address, borrower=borrower, settled=False
    )
    take = chain.auction_take.objects.create(
        order_index=event.order_index,
        auction_uid=auction.uid,
        pool_address=event.pool_address,
        taker=taker,
        amount=amount,
        collateral=collateral,
        auction_price=amount / collateral,
        bond_change=bond_change,
        is_reward=event.data["isReward"],
        block_number=event.block_number,
        block_datetime=event.block_datetime,
        transaction_hash=event.transaction_hash,
        collateral_token_price=event.collateral_token_price,
        quote_token_price=event.quote_token_price,
    )

    _update_auction(chain, auction.uid, event.block_number, last_take_price=take.auction_price)
    _update_kick_locked_amount(chain, auction.uid, take.is_reward, bond_change)


def process_bucket_take_event(chain, event):
    try:
        chain.auction_bucket_take.objects.get(order_index=event.order_index)
    except chain.auction_bucket_take.DoesNotExist:
        pass
    else:
        # If auction_bucket_take already exists, don't process it
        return

    borrower = event.data["borrower"].lower()

    # get taker from transaction
    transaction_info = chain.eth.get_transaction(event.transaction_hash)
    taker = transaction_info["from"].lower()

    amount = wad_to_decimal(event.data["amount"])
    collateral = wad_to_decimal(event.data["collateral"])
    bond_change = wad_to_decimal(event.data["bondChange"])

    auction = chain.auction.objects.get(
        pool_address=event.pool_address, borrower=borrower, settled=False
    )
    take = chain.auction_bucket_take.objects.create(
        order_index=event.order_index,
        auction_uid=auction.uid,
        pool_address=event.pool_address,
        taker=taker,
        index=event.data["index"],
        amount=amount,
        collateral=collateral,
        auction_price=amount / collateral,
        bond_change=bond_change,
        is_reward=event.data["isReward"],
        block_number=event.block_number,
        block_datetime=event.block_datetime,
        transaction_hash=event.transaction_hash,
        collateral_token_price=event.collateral_token_price,
        quote_token_price=event.quote_token_price,
    )

    _update_auction(chain, auction.uid, event.block_number, last_take_price=take.auction_price)
    _update_kick_locked_amount(chain, auction.uid, take.is_reward, bond_change)


def process_settle_event(chain, event):
    try:
        chain.auction_settle.objects.get(order_index=event.order_index)
    except chain.auction_settle.DoesNotExist:
        pass
    else:
        # If auction_settle already exists, don't process it
        return

    borrower = event.data["borrower"].lower()

    auction = chain.auction.objects.get(
        pool_address=event.pool_address, borrower=borrower, settled=False
    )
    chain.auction_settle.objects.create(
        order_index=event.order_index,
        auction_uid=auction.uid,
        pool_address=event.pool_address,
        settled_debt=wad_to_decimal(event.data["settledDebt"]),
        block_number=event.block_number,
        block_datetime=event.block_datetime,
        transaction_hash=event.transaction_hash,
        collateral_token_price=event.collateral_token_price,
        quote_token_price=event.quote_token_price,
    )

    _update_auction(chain, auction.uid, event.block_number)


def process_auction_settle_event(chain, event):
    try:
        chain.auction_auction_settle.objects.get(order_index=event.order_index)
    except chain.auction_auction_settle.DoesNotExist:
        pass
    else:
        # If auction_auction_settle already exists, don't process it
        return

    borrower = event.data["borrower"].lower()

    current_position = chain.current_wallet_position.objects.get(
        pool_address=event.pool_address, wallet_address=borrower, in_liquidation=True
    )
    auction = chain.auction.objects.get(
        pool_address=event.pool_address, borrower=borrower, settled=False
    )
    chain.auction_auction_settle.objects.create(
        order_index=event.order_index,
        auction_uid=auction.uid,
        pool_address=event.pool_address,
        collateral=wad_to_decimal(event.data["collateral"]),
        block_number=event.block_number,
        block_datetime=event.block_datetime,
        transaction_hash=event.transaction_hash,
        collateral_token_price=event.collateral_token_price,
        quote_token_price=event.quote_token_price,
    )

    auction.settled = True
    auction.settle_time = event.block_datetime
    auction.save()
    current_position.in_liquidation = False
    current_position.save()


def process_auction_nft_settle_event(chain, event):
    try:
        chain.auction_auction_nft_settle.objects.get(order_index=event.order_index)
    except chain.auction_auction_nft_settle.DoesNotExist:
        pass
    else:
        # If auction_auction_nft_settle already exists, don't process it
        return

    borrower = event.data["borrower"].lower()

    current_position = chain.current_wallet_position.objects.get(
        pool_address=event.pool_address, wallet_address=borrower, in_liquidation=True
    )
    auction = chain.auction.objects.get(
        pool_address=event.pool_address, borrower=borrower, settled=False
    )
    chain.auction_auction_nft_settle.objects.create(
        order_index=event.order_index,
        auction_uid=auction.uid,
        pool_address=event.pool_address,
        index=event.data["index"],
        collateral=wad_to_decimal(event.data["collateral"]),
        block_number=event.block_number,
        block_datetime=event.block_datetime,
        transaction_hash=event.transaction_hash,
        collateral_token_price=event.collateral_token_price,
        quote_token_price=event.quote_token_price,
    )

    auction.settled = True
    auction.settle_time = event.block_datetime
    auction.save()
    current_position.in_liquidation = False
    current_position.save()


def calculate_current_auction_price(kick_datetime, reserves):
    seconds = (datetime.now() - kick_datetime).total_seconds()

    hours = seconds // 3600
    if hours > 72:
        return None

    hours_component = Decimal("0.5") ** Decimal(str(hours))
    minute_half_life = Decimal("0.988514020352896135356867505")  # 0.5^(1/60)
    minutes_component = Decimal(str(math.pow(minute_half_life, seconds % 3600 // 60)))

    initial_price = Decimal("1000000000") / reserves

    return initial_price * (hours_component * minutes_component)
