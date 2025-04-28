from datetime import date, datetime
from decimal import Decimal

from eth_abi import abi
from eth_abi.exceptions import InsufficientDataBytes
from web3 import Web3

from ajna.constants import ERC20, ERC721
from ajna.utils.db import fetch_all, fetch_one
from ajna.utils.utils import chunks, compute_order_index, datetime_to_next_full_hour
from ajna.utils.wad import wad_to_decimal

VOLUME_SQL = """
    SELECT
          pool_address
        , SUM(
            CASE
                WHEN name = 'AddCollateral' THEN
                    CAST(data->>'amount' AS NUMERIC) / 1e18 * collateral_token_price
                WHEN name = 'RemoveCollateral' THEN
                    CAST(data->>'amount' AS NUMERIC) / 1e18 * collateral_token_price
                WHEN name = 'AddQuoteToken' THEN
                    CAST(data->>'amount' AS NUMERIC) / 1e18 * quote_token_price
                WHEN name = 'RemoveQuoteToken' THEN
                    CAST(data->>'amount' AS NUMERIC) / 1e18 * quote_token_price
                WHEN name = 'DrawDebt' THEN
                    CAST(data->>'amountBorrowed' AS NUMERIC) / 1e18 * quote_token_price +
                    CAST(data->>'collateralPledged' AS NUMERIC) / 1e18 * collateral_token_price
                WHEN name = 'DrawDebtNFT' THEN
                    CAST(data->>'amountBorrowed' AS NUMERIC) / 1e18 * quote_token_price
                WHEN name = 'RepayDebt' THEN
                    CAST(data->>'quoteRepaid' AS NUMERIC) / 1e18 * quote_token_price +
                    CAST(data->>'collateralPulled' AS NUMERIC) / 1e18 * collateral_token_price
            END
          ) AS amount
    FROM {pool_event_table}
    WHERE block_datetime::DATE = %s
        AND name IN (
            'AddCollateral',
            'RemoveCollateral',
            'AddQuoteToken',
            'RemoveQuoteToken',
            'DrawDebt',
            'DrawDebtNFT',
            'RepayDebt'
        )
        {filters}
    GROUP BY 1
"""


def save_all_pools_volume_for_date(chain, dt):
    if not isinstance(dt, date):
        raise TypeError
    sql = VOLUME_SQL.format(pool_event_table=chain.pool_event._meta.db_table, filters="")

    sql_vars = [dt]

    volumes = fetch_all(sql, sql_vars)

    for volume in volumes:
        chain.pool_volume_snapshot.objects.update_or_create(
            pool_address=volume["pool_address"],
            date=dt,
            defaults={
                "amount": volume["amount"] or Decimal("0"),
            },
        )


class BasePoolManager:
    def __init__(self):
        self._token_info = {}
        self.pool_factory_start_block = (
            self._chain.erc20_pool_factory_start_block
            if self.erc == ERC20
            else self._chain.erc721_pool_factory_start_block
        )
        self.pool_factory_address = (
            self._chain.erc20_pool_factory_address
            if self.erc == ERC20
            else self._chain.erc721_pool_factory_address
        )

    def token_info(self, token_address):
        if token_address not in self._token_info:
            token = self._chain.token.objects.only("decimals", "underlying_price", "symbol").get(
                underlying_address=token_address
            )

            info = {
                "decimals": token.decimals,
                "price": token.underlying_price,
                "symbol": token.symbol,
            }

            self._token_info[token_address] = info

        return self._token_info[token_address]

    def _create_erc20_token(self, token_address):
        if self._chain.token.objects.filter(underlying_address=token_address).exists():
            return False

        # Some tokens (like MKR) are not really erc20 compatible but are still
        # considered to be erc20, which have name and symbol instead of string,
        # encoded as bytes, so we request both, and then figure out which one we
        # need
        calls = [
            (
                token_address,
                ["name()(string)"],
                ["name", None],
            ),
            (
                token_address,
                ["name()(bytes32)"],
                ["nameBytes", None],
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
            (
                token_address,
                ["symbol()(bytes32)"],
                ["symbolBytes", None],
            ),
        ]

        data = self._chain.multicall(calls)

        symbol = (
            data["symbol"] if data["symbol"] else Web3.to_text(data["symbolBytes"].strip(bytes(1)))
        )
        name = data["name"] if data["name"] else Web3.to_text(data["nameBytes"].strip(bytes(1)))

        self._chain.token.objects.create(
            underlying_address=token_address,
            symbol=symbol,
            name=name,
            decimals=data["decimals"],
            erc=ERC20,
        )
        return True

    def _fetch_new_pool_created_events(self):
        sql = f"""
            SELECT
                pe.block_number
            FROM {self._chain.pool_event._meta.db_table} pe
            WHERE pe.name = 'PoolCreated'
                AND pe.data->>'erc' = %s
            ORDER BY pe.block_number DESC
            LIMIT 1
        """

        data = fetch_one(sql, [self.erc])

        if data:
            from_block_number = data["block_number"] + 1
        else:
            from_block_number = self.pool_factory_start_block

        events = self._chain.get_events_for_contract_topics(
            self.pool_factory_address,
            ["0x83a48fbcfc991335314e74d0496aab6a1987e992ddc85dddbcc4d6dd6ef2e9fc"],
            from_block_number,
        )
        yield from events

    def _fetch_and_calculate_additional_pool_data(self, pools_data, block_number=None):
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
                        pool_data["quote_token_address"],
                        ["balanceOf(address)(uint256)", pool_address],
                        [f"{pool_address}:quoteTokenBalance", None],
                    ),
                    (
                        pool_data["collateral_token_address"],
                        ["balanceOf(address)(uint256)", pool_address],
                        [f"{pool_address}:collateralTokenBalance", None],
                    ),
                ]
            )

        data = self._chain.multicall(calls, block_identifier=block_number)

        for pool_address, pool_data in pools_data.items():
            meaningful_deposit = wad_to_decimal(data[f"{pool_address}:depositUpToIndex"])
            quote_token_balance = data[f"{pool_address}:quoteTokenBalance"]
            collateral_token_balance = data[f"{pool_address}:collateralTokenBalance"]

            utilization = None
            lend_rate = Decimal("0")
            if meaningful_deposit:
                utilization = pool_data["debt"] / meaningful_deposit
                lend_rate = (
                    pool_data["borrow_rate"] * pool_data["lender_interest_margin"] * utilization
                )

            pool_data["current_meaningful_utilization"] = utilization
            pool_data["lend_rate"] = lend_rate

            # Need to multiply token balance with token scale so that we get to the WAD
            # value, as not all tokens use 18 decimals
            quote_token = self.token_info(pool_data["quote_token_address"])
            quote_token_scale = Decimal("1e{}".format(18 - quote_token["decimals"]))
            pool_data["quote_token_balance"] = wad_to_decimal(
                quote_token_balance * quote_token_scale
            )
            collateral_token = self.token_info(pool_data["collateral_token_address"])
            collateral_scale = Decimal("1e{}".format(18 - collateral_token["decimals"]))
            pool_data["collateral_token_balance"] = wad_to_decimal(
                collateral_token_balance * collateral_scale
            )

            del pool_data["lender_interest_margin"]

    def _fetch_pools_data(self, pool_addresses, block_number=None):
        calls = []
        for pool_address in pool_addresses:
            calls.extend(
                [
                    (
                        self._chain.pool_info_address,
                        [
                            ("poolLoansInfo(address)((uint256,uint256,address,uint256,uint256))"),
                            pool_address,
                        ],
                        [f"{pool_address}:loansInfo", None],
                    ),
                    (
                        self._chain.pool_info_address,
                        [
                            (
                                "poolPricesInfo(address)("
                                "(uint256,uint256,uint256,uint256,uint256,uint256))"
                            ),
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
                        self._chain.pool_info_address,
                        [
                            "lenderInterestMargin(address)(uint256)",
                            pool_address,
                        ],
                        [f"{pool_address}:lenderInterestMargin", None],
                    ),
                    (
                        self._chain.pool_info_address,
                        [
                            "momp(address)(uint256)",
                            pool_address,
                        ],
                        [f"{pool_address}:momp", None],
                    ),
                    (
                        self._chain.pool_info_address,
                        [
                            (
                                "poolReservesInfo(address)("
                                "(uint256,uint256,uint256,uint256,uint256))"
                            ),
                            pool_address,
                        ],
                        [f"{pool_address}:poolReservesInfo", None],
                    ),
                    (
                        self._chain.pool_info_address,
                        [
                            ("poolUtilizationInfo(address)((uint256,uint256,uint256,uint256))"),
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
                        self._chain.pool_info_address,
                        [
                            "borrowFeeRate(address)(uint256)",
                            pool_address,
                        ],
                        [f"{pool_address}:borrowFeeRate", None],
                    ),
                    (
                        self._chain.pool_info_address,
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

        data = self._chain.multicall(calls, block_identifier=block_number)

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
            }

        # NOTE: this function mutates pools_data
        self._fetch_and_calculate_additional_pool_data(pools_data)

        return pools_data

    def _fetch_and_save_data(self, pool_addresses):
        dt = datetime.now()

        # Put pools into more managable chunks so that we don't use too much ram and
        # we don't download half of the blockchain in one multicall call.
        pool_chunks = chunks(pool_addresses, 100)
        for addresses in pool_chunks:
            pools_data = self._fetch_pools_data(pool_addresses)
            for address in addresses:
                pool_data = pools_data[address]
                # Force address to be lowercase just in case it wasn't already
                address = address.lower()

                pool_data["volume_today"] = self._calculate_volume_for_pool_for_date(
                    address, dt.date()
                )
                collateral_token = self.token_info(pool_data["collateral_token_address"])
                quote_token = self.token_info(pool_data["quote_token_address"])

                try:
                    pool = self._chain.pool.objects.get(address=address)
                except self._chain.pool.DoesNotExist:
                    created_event = self._chain.pool_event.objects.get(
                        pool_address=address, name="PoolCreated"
                    )

                    pool = self._chain.pool(
                        address=address,
                        created_at_block_number=created_event.block_number,
                        created_at_timestamp=int(created_event.block_datetime.timestamp()),
                        erc=self.erc,
                        allowed_token_ids=created_event.data.get("token_ids"),
                        collateral_token_symbol=collateral_token["symbol"],
                        quote_token_symbol=quote_token["symbol"],
                        total_ajna_burned=Decimal("0"),
                    )

                for field, value in pool_data.items():
                    setattr(pool, field, value)

                pool.datetime = datetime.now()
                pool.save()

                # Add fields that we need for pool snapshot
                pool_data["collateral_token_price"] = collateral_token["price"]
                pool_data["quote_token_price"] = quote_token["price"]

                collateralization = None
                if (
                    pool_data["t0debt"] > 0
                    and pool_data["pending_inflator"] > 0
                    and quote_token["price"]
                    and collateral_token["price"]
                ):
                    collateralization = (
                        pool_data["pledged_collateral"] * collateral_token["price"]
                    ) / (pool_data["t0debt"] * pool_data["pending_inflator"] * quote_token["price"])

                pool_data["collateralization"] = collateralization

                self._chain.pool_snapshot.objects.update_or_create(
                    address=address,
                    datetime=datetime_to_next_full_hour(dt),
                    defaults=pool_data,
                )

    def fetch_and_save_pools_data(self):
        pool_addresses = list(
            self._chain.pool_event.objects.filter(
                name="PoolCreated", data__erc=self.erc
            ).values_list("pool_address", flat=True)
        )

        self._fetch_and_save_data(pool_addresses)


class PoolERC20Manager(BasePoolManager):
    def __init__(self, chain):
        self._chain = chain
        self.erc = ERC20
        super().__init__()

    def _calculate_volume_for_pool_for_date(self, pool_address, dt):
        if not isinstance(dt, date):
            raise TypeError
        sql = VOLUME_SQL.format(
            pool_event_table=self._chain.pool_event._meta.db_table,
            filters="AND pool_address = %s",
        )

        sql_vars = [dt, pool_address]
        volume = fetch_one(sql, sql_vars)

        return volume["amount"] if volume and volume["amount"] else Decimal("0")

    def fetch_and_save_pool_created_events(self):
        token_created = False
        events = self._fetch_new_pool_created_events()
        for event in events:
            transaction_info = self._chain.eth.get_transaction(event["transactionHash"])

            collateral_token_address, quote_token_address, _ = abi.decode(
                ["address", "address", "uint256"], transaction_info.input[4:]
            )

            collateral_token_address = collateral_token_address.lower()
            quote_token_address = quote_token_address.lower()

            order_index = compute_order_index(
                event["blockNumber"], event["transactionIndex"], event["logIndex"]
            )
            block_datetime = self._chain.get_block_datetime(event["blockNumber"])
            pool_data = dict(event["args"])
            pool_data["erc"] = self.erc
            pool_data["collateral_token_address"] = collateral_token_address
            pool_data["quote_token_address"] = quote_token_address.lower()

            self._chain.pool_event.objects.create(
                pool_address=event["args"]["pool_"].lower(),
                block_number=event["blockNumber"],
                block_datetime=block_datetime,
                order_index=order_index,
                transaction_hash=event["transactionHash"].to_0x_hex(),
                name=event["event"],
                data=pool_data,
            )

            collateral_token_created = self._create_erc20_token(collateral_token_address)
            quote_token_created = self._create_erc20_token(quote_token_address)

            if collateral_token_created or quote_token_created:
                token_created = True

        if token_created:
            self._chain.celery_tasks.fetch_market_price_task.delay()


class PoolERC721Manager(BasePoolManager):
    def __init__(self, chain):
        self._chain = chain
        self.erc = ERC721
        super().__init__()

    def _create_erc721_token(self, token_address):
        if self._chain.token.objects.filter(underlying_address=token_address).exists():
            return False

        calls = [
            (
                token_address,
                ["name()(string)"],
                ["name", None],
            ),
            (
                token_address,
                ["symbol()(string)"],
                ["symbol", None],
            ),
        ]

        data = self._chain.multicall(calls)

        self._chain.token.objects.create(
            underlying_address=token_address,
            symbol=data["symbol"],
            name=data["name"],
            decimals=18,
            erc=ERC721,
        )
        return True

    def _calculate_volume_for_pool_for_date(self, pool_address, dt):
        if not isinstance(dt, date):
            raise TypeError
        sql = VOLUME_SQL.format(
            pool_event_table=self._chain.pool_event._meta.db_table,
            filters="AND pool_address = %s",
        )

        sql_vars = [dt, pool_address]
        volume = fetch_one(sql, sql_vars)

        return volume["amount"] if volume and volume["amount"] else Decimal("0")

    def fetch_and_save_pool_created_events(self):
        token_created = False
        events = self._fetch_new_pool_created_events()
        for event in events:
            transaction_info = self._chain.eth.get_transaction(event["transactionHash"])

            try:
                (
                    collateral_token_address,
                    quote_token_address,
                    token_ids,
                    _,
                ) = abi.decode(
                    ["address", "address", "uint256[]", "uint256"],
                    transaction_info.input[4:],
                )
            except InsufficientDataBytes:
                token_ids = None
                collateral_token_address, quote_token_address, _ = abi.decode(
                    ["address", "address", "uint256"], transaction_info.input[4:]
                )

            collateral_token_address = collateral_token_address.lower()
            quote_token_address = quote_token_address.lower()

            order_index = compute_order_index(
                event["blockNumber"], event["transactionIndex"], event["logIndex"]
            )
            block_datetime = self._chain.get_block_datetime(event["blockNumber"])
            pool_data = dict(event["args"])
            pool_data["erc"] = self.erc
            pool_data["collateral_token_address"] = collateral_token_address
            pool_data["quote_token_address"] = quote_token_address.lower()
            pool_data["token_ids"] = list(token_ids) if token_ids else None

            self._chain.pool_event.objects.create(
                pool_address=event["args"]["pool_"].lower(),
                block_number=event["blockNumber"],
                block_datetime=block_datetime,
                order_index=order_index,
                transaction_hash=event["transactionHash"].to_0x_hex(),
                name=event["event"],
                data=pool_data,
            )

            collateral_token_created = self._create_erc721_token(collateral_token_address)
            quote_token_created = self._create_erc20_token(quote_token_address)

            if collateral_token_created or quote_token_created:
                token_created = True

        if token_created:
            self._chain.celery_tasks.fetch_market_price_task.delay()
