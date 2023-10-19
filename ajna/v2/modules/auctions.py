import hashlib
import logging

from ajna.utils.wad import wad_to_decimal

log = logging.getLogger(__name__)


def _generate_auction_uid(pool_address, borrower, block_number):
    key = "{}_{}_{}".format(pool_address, borrower, block_number).encode("utf-8")
    return hashlib.md5(key).hexdigest()


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
                "address,address,bool))",
                auction.borrower,
            ],
            ["auctionInfo", None],
        ),
        (
            chain.pool_info_address,
            [
                "auctionStatus(address,address)("
                "(uint256,uint256,uint256,bool,uint256,uint256))",
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
        chain.auction_kick.objects.filter(auction_uid=auction_uid)
        .order_by("-block_number")
        .first()
    )
    if is_reward:
        kick.locked = kick.locked + locked_change
    else:
        kick.locked = kick.locked - locked_change
    kick.save()


def process_kick_event(chain, event):
    borrower = event.data["borrower"].lower()
    bond = wad_to_decimal(event.data["bond"])

    # get kicker from transaction
    transaction_info = chain.eth.get_transaction(event.transaction_hash)
    kicker = transaction_info["from"].lower()

    calls = [
        (
            event.pool_address,
            [
                "auctionInfo(address)("
                "(address,uint256,uint256,uint256,uint256,uint256,address,"
                "address,address,bool))",
                event.data["borrower"],
            ],
            ["auctionInfo", None],
        ),
        (
            chain.pool_info_address,
            [
                "auctionStatus(address,address)("
                "(uint256,uint256,uint256,bool,uint256,uint256))",
                event.pool_address,
                event.data["borrower"],
            ],
            ["auctionStatus", None],
        ),
    ]

    mc_data = chain.multicall(calls, block_identifier=event.block_number)

    kick_momp = wad_to_decimal(mc_data["auctionInfo"][4])
    starting_price = wad_to_decimal(mc_data["auctionStatus"][4])

    kick = chain.auction_kick.objects.create(
        order_index=event.order_index,
        auction_uid=_generate_auction_uid(
            event.pool_address, borrower, event.block_number
        ),
        pool_address=event.pool_address,
        borrower=borrower,
        debt=wad_to_decimal(event.data["debt"]),
        collateral=wad_to_decimal(event.data["collateral"]),
        bond=bond,
        locked=bond,
        block_number=event.block_number,
        block_datetime=event.block_datetime,
        kicker=kicker,
        kick_momp=kick_momp,
        starting_price=starting_price,
        collateral_token_price=event.collateral_token_price,
        quote_token_price=event.quote_token_price,
    )

    _create_auction(chain, event.pool_address, borrower, kick)


def process_take_event(chain, event):
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
        collateral_token_price=event.collateral_token_price,
        quote_token_price=event.quote_token_price,
    )

    _update_auction(
        chain, auction.uid, event.block_number, last_take_price=take.auction_price
    )
    _update_kick_locked_amount(chain, auction.uid, take.is_reward, bond_change)


def process_bucket_take_event(chain, event):
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
        collateral_token_price=event.collateral_token_price,
        quote_token_price=event.quote_token_price,
    )

    _update_auction(
        chain, auction.uid, event.block_number, last_take_price=take.auction_price
    )
    _update_kick_locked_amount(chain, auction.uid, take.is_reward, bond_change)


def process_settle_event(chain, event):
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
        collateral_token_price=event.collateral_token_price,
        quote_token_price=event.quote_token_price,
    )

    _update_auction(chain, auction.uid, event.block_number)


def process_auction_settle_event(chain, event):
    borrower = event.data["borrower"].lower()

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
        collateral_token_price=event.collateral_token_price,
        quote_token_price=event.quote_token_price,
    )

    auction.settled = True
    auction.settle_time = event.block_datetime
    auction.save()
