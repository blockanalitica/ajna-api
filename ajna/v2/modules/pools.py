from datetime import datetime
from decimal import Decimal

from ajna.utils.utils import chunks, compute_order_index, datetime_to_next_full_hour
from ajna.utils.wad import wad_to_decimal


def fetch_new_pools(chain):
    last_event = chain.pool_event.objects.all().order_by("-order_index").first()

    from_block_number = chain.erc20_pool_factory_start_block

    if last_event:
        from_block_number = last_event.block_number + 1

    events = chain.get_events_for_contract_topics(
        chain.erc20_pool_factory_address,
        ["0x83a48fbcfc991335314e74d0496aab6a1987e992ddc85dddbcc4d6dd6ef2e9fc"],
        from_block_number,
    )
    for event in events:
        order_index = compute_order_index(
            event["blockNumber"], event["transactionIndex"], event["logIndex"]
        )
        block_info = chain.get_block_info(event["blockNumber"])
        block_datetime = datetime.fromtimestamp(block_info["timestamp"])
        chain.pool_event.objects.create(
            pool_address=event["args"]["pool_"].lower(),
            block_number=event["blockNumber"],
            block_datetime=block_datetime,
            order_index=order_index,
            transaction_hash=event["transactionHash"].hex(),
            name=event["event"],
            data=dict(event["args"]),
        )


def _fetch_and_calculate_additional_pool_data(chain, pools_data, block_number=None):
    """
    NOTE: This function mutates pools_data dictionary that is passed in this function
    as parameter!
    """
    calls = []
    for pool_address, pool_data in pools_data.items():
        calls.extend(
            [
                (
                    pool_address,
                    [
                        "depositUpToIndex(uint256)(uint256)",
                        max(pool_data["lup_index"], pool_data["htp_index"]),
                    ],
                    [f"{pool_address}:depositUpToIndex", None],
                ),
                (
                    pool_address,
                    [
                        "burnInfo(uint256)((uint256,uint256,uint256))",
                        pool_data["burn_epoch"],
                    ],
                    [f"{pool_address}:burnInfo", None],
                ),
                (
                    pool_data["quote_token_address"],
                    ["balanceOf(address)(uint256)", pool_address],
                    [f"{pool_address}:quoteTokenBalance", None],
                ),
                (
                    pool_data["collateral_token_address"],
                    ["balanceOf(address)(uint256)", pool_address],
                    [f"{pool_address}:collateralTokenBalance", None],
                ),
                (
                    pool_address,
                    ["quoteTokenScale()(uint256)"],
                    [f"{pool_address}:quoteTokenScale", None],
                ),
                (
                    pool_address,
                    ["collateralScale()(uint256)"],
                    [f"{pool_address}:collateralScale", None],
                ),
            ]
        )

    data = chain.multicall(calls, block_identifier=block_number)

    for pool_address, pool_data in pools_data.items():
        meaningful_deposit = wad_to_decimal(data[f"{pool_address}:depositUpToIndex"])
        burn_info = data[f"{pool_address}:burnInfo"]
        quote_token_balance = data[f"{pool_address}:quoteTokenBalance"]
        quote_token_scale = data[f"{pool_address}:quoteTokenScale"]
        collateral_token_balance = data[f"{pool_address}:collateralTokenBalance"]
        collateral_scale = data[f"{pool_address}:collateralScale"]

        utilization = None
        lend_rate = Decimal("0")
        if meaningful_deposit:
            utilization = pool_data["debt"] / meaningful_deposit
            lend_rate = (
                pool_data["borrow_rate"]
                * pool_data["lender_interest_margin"]
                * utilization
            )

        pool_data["current_meaningful_utilization"] = utilization
        pool_data["lend_rate"] = lend_rate
        pool_data["total_ajna_burned"] = wad_to_decimal(burn_info[2])

        # Need to multiply token balance with token scale so that we get to the WAD
        # value, as not all tokens use 18 decimals
        pool_data["quote_token_balance"] = wad_to_decimal(
            quote_token_balance * quote_token_scale
        )
        pool_data["collateral_token_balance"] = wad_to_decimal(
            collateral_token_balance * collateral_scale
        )

        del pool_data["lender_interest_margin"]


def _fetch_pools_data(chain, pool_addresses, block_number=None):
    calls = []
    for pool_address in pool_addresses:
        calls.extend(
            [
                (
                    chain.pool_info_address,
                    [
                        "poolLoansInfo(address)((uint256,uint256,address,uint256,uint256))",
                        pool_address,
                    ],
                    [f"{pool_address}:loansInfo", None],
                ),
                (
                    chain.pool_info_address,
                    [
                        "poolPricesInfo(address)((uint256,uint256,uint256,uint256,uint256,uint256))",
                        pool_address,
                    ],
                    [f"{pool_address}:pricesInfo", None],
                ),
                (
                    pool_address,
                    ["interestRateInfo()((uint256,uint256))"],
                    [f"{pool_address}:interestRateInfo", None],
                ),
                (
                    pool_address,
                    ["debtInfo()((uint256,uint256,uint256,uint256))"],
                    [f"{pool_address}:debtInfo", None],
                ),
                (
                    chain.pool_info_address,
                    [
                        "lenderInterestMargin(address)(uint256)",
                        pool_address,
                    ],
                    [f"{pool_address}:lenderInterestMargin", None],
                ),
                (
                    chain.pool_info_address,
                    [
                        "momp(address)(uint256)",
                        pool_address,
                    ],
                    [f"{pool_address}:momp", None],
                ),
                (
                    chain.pool_info_address,
                    [
                        "poolReservesInfo(address)((uint256,uint256,uint256,uint256,uint256))",
                        pool_address,
                    ],
                    [f"{pool_address}:poolReservesInfo", None],
                ),
                (
                    chain.pool_info_address,
                    [
                        "poolUtilizationInfo(address)((uint256,uint256,uint256,uint256))",
                        pool_address,
                    ],
                    [f"{pool_address}:poolUtilizationInfo", None],
                ),
                (
                    pool_address,
                    ["inflatorInfo()((uint256,uint256))"],
                    [f"{pool_address}:inflatorInfo", None],
                ),
                (
                    chain.pool_info_address,
                    [
                        "borrowFeeRate(address)(uint256)",
                        pool_address,
                    ],
                    [f"{pool_address}:borrowFeeRate", None],
                ),
                (
                    chain.pool_info_address,
                    [
                        "unutilizedDepositFeeRate(address)(uint256)",
                        pool_address,
                    ],
                    [f"{pool_address}:unutilizedDepositFeeRate", None],
                ),
                (
                    pool_address,
                    ["pledgedCollateral()(uint256)"],
                    [f"{pool_address}:pledgedCollateral", None],
                ),
                (
                    pool_address,
                    ["reservesInfo()((uint256,uint256,uint256,uint256))"],
                    [f"{pool_address}:reservesInfo", None],
                ),
                (
                    pool_address,
                    ["currentBurnEpoch()(uint256)"],
                    [f"{pool_address}:currentBurnEpoch", None],
                ),
                (
                    pool_address,
                    ["collateralAddress()(address)"],
                    [f"{pool_address}:collateralAddress", None],
                ),
                (
                    pool_address,
                    ["quoteTokenAddress()(address)"],
                    [f"{pool_address}:quoteTokenAddress", None],
                ),
            ]
        )

    data = chain.multicall(calls, block_identifier=block_number)

    pools_data = {}
    for pool_address in pool_addresses:
        loans_info = data[f"{pool_address}:loansInfo"]
        prices_info = data[f"{pool_address}:pricesInfo"]
        interest_rate_info = data[f"{pool_address}:interestRateInfo"]
        debt_info = data[f"{pool_address}:debtInfo"]
        lim = data[f"{pool_address}:lenderInterestMargin"]
        momp = data[f"{pool_address}:momp"]
        pool_reserves_info = data[f"{pool_address}:poolReservesInfo"]
        utilization_info = data[f"{pool_address}:poolUtilizationInfo"]
        inflator_info = data[f"{pool_address}:inflatorInfo"]
        borrow_fee_rate = data[f"{pool_address}:borrowFeeRate"]
        deposit_fee_rate = data[f"{pool_address}:unutilizedDepositFeeRate"]
        pledged_collateral = data[f"{pool_address}:pledgedCollateral"]
        reserves_info = data[f"{pool_address}:reservesInfo"]
        current_burn_epoch = data[f"{pool_address}:currentBurnEpoch"]

        collateral_address = data[f"{pool_address}:collateralAddress"]
        quote_token_address = data[f"{pool_address}:quoteTokenAddress"]

        pending_debt = wad_to_decimal(debt_info[0])
        pending_inflator = wad_to_decimal(loans_info[3])
        pool_size = wad_to_decimal(loans_info[0])

        utilization = Decimal("0")
        if pool_size > 0:
            utilization = min(pending_debt / pool_size, Decimal("1"))

        pools_data[pool_address] = {
            "lender_interest_margin": wad_to_decimal(lim),
            "collateral_token_address": collateral_address.lower(),
            "quote_token_address": quote_token_address.lower(),
            "pool_size": pool_size,
            "debt": pending_debt,
            "t0debt": round(pending_debt / pending_inflator, 18),
            "inflator": wad_to_decimal(inflator_info[0]),
            "pending_inflator": pending_inflator,
            "borrow_rate": wad_to_decimal(interest_rate_info[0]),
            "borrow_fee_rate": wad_to_decimal(borrow_fee_rate),
            "deposit_fee_rate": wad_to_decimal(deposit_fee_rate),
            "pledged_collateral": wad_to_decimal(pledged_collateral),
            "total_interest_earned": wad_to_decimal(reserves_info[3]),
            "loans_count": loans_info[1],
            "max_borrower": loans_info[2],
            "hpb": wad_to_decimal(prices_info[0]),
            "hpb_index": prices_info[1],
            "htp": wad_to_decimal(prices_info[2]),
            "htp_index": prices_info[3],
            "lup": wad_to_decimal(prices_info[4]),
            "lup_index": prices_info[5],
            "momp": wad_to_decimal(momp),
            "reserves": wad_to_decimal(pool_reserves_info[0]),
            "claimable_reserves": wad_to_decimal(pool_reserves_info[1]),
            "claimable_reserves_remaining": wad_to_decimal(pool_reserves_info[2]),
            "burn_epoch": current_burn_epoch,
            "min_debt_amount": wad_to_decimal(utilization_info[0]),
            "utilization": utilization,
            "actual_utilization": wad_to_decimal(utilization_info[2]),
            "target_utilization": wad_to_decimal(utilization_info[3]),
            # "total_bond_escrowed": pool_data["totalBondEscrowed"],
        }

    # NOTE: this function mutates pools_data
    _fetch_and_calculate_additional_pool_data(chain, pools_data)

    return pools_data


def _fetch_token_data(chain, token_address):
    calls = [
        (
            token_address,
            [
                "name()(string)",
            ],
            ["name", None],
        ),
        (
            token_address,
            ["decimals()(uint8)"],
            ["decimals", None],
        ),
        (
            token_address,
            ["symbol()(string)"],
            ["symbol", None],
        ),
    ]

    return chain.multicall(calls)


def fetch_and_save_pool_data(chain, pool_addresses):
    dt = datetime.now()

    token_created = False
    # Put pools into more managable chunks so that we don't use too much ram and
    # so that we don't download half of the blockchain in one multicall call.
    pool_chunks = chunks(pool_addresses, 100)
    for addresses in pool_chunks:
        # Force addresses to be lowercase, just in case they aren't already
        pools_data = _fetch_pools_data(chain, pool_addresses)
        for address in addresses:
            pool_data = pools_data[address]
            # Force address to be lowercase just in case it wasn't already
            address = address.lower()

            try:
                pool = chain.pool.objects.get(address=address)
            except chain.pool.DoesNotExist:
                created_event = chain.pool_event.objects.get(
                    pool_address=address, name="PoolCreated"
                )

                pool = chain.pool(
                    address=address,
                    created_at_block_number=created_event.block_number,
                    created_at_timestamp=int(created_event.block_datetime.timestamp()),
                )

            for field, value in pool_data.items():
                setattr(pool, field, value)

            pool.datetime = datetime.now()
            pool.save()

            # Check if collateral token exists, otherwise create it
            try:
                collateral_token = chain.token.objects.get(
                    underlying_address=pool.collateral_token_address
                )
            except chain.token.DoesNotExist:
                collateral_token_data = _fetch_token_data(
                    chain, pool.collateral_token_address
                )
                collateral_token = chain.token.objects.create(
                    underlying_address=pool.collateral_token_address,
                    symbol=collateral_token_data["symbol"],
                    name=collateral_token_data["name"],
                    decimals=collateral_token_data["decimals"],
                    # TODO: change is_erc721 to token type and store correct value
                    is_erc721=False,
                )
                token_created = True

            # Check if quote token exists, otherwise create it
            try:
                quote_token = chain.token.objects.get(
                    underlying_address=pool.quote_token_address
                )
            except chain.token.DoesNotExist:
                quote_token_data = _fetch_token_data(chain, pool.quote_token_address)
                quote_token = chain.token.objects.create(
                    underlying_address=pool.quote_token_address,
                    symbol=quote_token_data["symbol"],
                    name=quote_token_data["name"],
                    decimals=quote_token_data["decimals"],
                    # TODO: change is_erc721 to token type and store correct value
                    is_erc721=False,
                )
                token_created = True

            # Add fields that we need for pool snapshot
            pool_data["collateral_token_price"] = collateral_token.underlying_price
            pool_data["quote_token_price"] = quote_token.underlying_price

            collateralization = None
            if (
                pool_data["t0debt"] > 0
                and pool_data["pending_inflator"] > 0
                and quote_token.underlying_price
                and collateral_token.underlying_price
            ):
                collateralization = (
                    pool_data["pledged_collateral"] * collateral_token.underlying_price
                ) / (
                    pool_data["t0debt"]
                    * pool_data["pending_inflator"]
                    * quote_token.underlying_price
                )

            pool_data["collateralization"] = collateralization

            chain.pool_snapshot.objects.update_or_create(
                address=address,
                datetime=datetime_to_next_full_hour(dt),
                defaults=pool_data,
            )

    if token_created:
        chain.celery_tasks.fetch_market_price_task.delay()
