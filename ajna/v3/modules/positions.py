import contextlib
import logging
from collections import defaultdict
from decimal import Decimal

from django.db import IntegrityError, connection

from ajna.utils.db import fetch_one
from ajna.utils.wad import wad_to_decimal

from .auctions import (
    process_auction_settle_event,
    process_bucket_take_event,
    process_kick_event,
    process_settle_event,
    process_take_event,
)
from .reserve_auctions import (
    process_kick_reserve_auction_event,
    process_reserve_auction_event,
)

log = logging.getLogger(__name__)


class EventProcessor:
    def __init__(self, chain):
        self._chain = chain

        self._block_datetimes = {}

        self._wallet_supply = defaultdict(Decimal)
        self._data_to_update = defaultdict(
            lambda: defaultdict(
                lambda: {
                    "wallets": set(),
                    "buckets": defaultdict(set),
                }
            )
        )

    def _build_wallets_and_buckets_to_update(self, events):
        for event in events:
            pool_data = self._data_to_update[event.block_number][event.pool_address]
            self._block_datetimes[event.block_number] = event.block_datetime

            if event.wallet_addresses:
                pool_data["wallets"].update(event.wallet_addresses)

            match event.name:
                case "AddQuoteToken" | "RemoveQuoteToken":
                    pool_data["buckets"][event.data["index"]].add(
                        event.wallet_addresses[0]
                    )

                case "MoveQuoteToken":
                    pool_data["buckets"][event.data["from"]].add(
                        event.wallet_addresses[0]
                    )
                    pool_data["buckets"][event.data["to"]].add(
                        event.wallet_addresses[0]
                    )

                case "AddCollateral" | "RemoveCollateral" | "AddCollateralNFT":
                    pool_data["buckets"][event.data["index"]].add(
                        event.wallet_addresses[0]
                    )

                case "BucketTake":
                    bucket_index = event.data["index"]
                    wallets = set(
                        self._chain.wallet_bucket_state.objects.filter(
                            pool_address=event.pool_address,
                            bucket_index=bucket_index,
                        ).values_list("wallet_address", flat=True)
                    )

                    pool_data["buckets"][bucket_index].update(wallets)
                case "TransferLP":
                    for bucket_index in event.data["indexes"]:
                        pool_data["buckets"][bucket_index].update(
                            event.wallet_addresses
                        )

                case "IncreaseLPAllowance":
                    for bucket_index in event.data["indexes"]:
                        pool_data["buckets"][bucket_index].update(
                            event.wallet_addresses
                        )

                case "BucketBankruptcy":
                    bucket_index = event.data["index"]
                    if bucket_index not in pool_data["buckets"]:
                        # Add bucket index to the buckets without any wallets so that
                        # we update the bucket itself
                        pool_data["buckets"][bucket_index] = set()

    def _save_buckets(self, block_number, to_update, results):
        for pool_address, data in to_update.items():
            for bucket_index, wallet_addresses in data["buckets"].items():
                # Handle wallet buckets
                for wallet_address in wallet_addresses:
                    info = results[f"{pool_address}:{bucket_index}:{wallet_address}"]
                    try:
                        self._chain.wallet_bucket_state.objects.create(
                            wallet_address=wallet_address,
                            pool_address=pool_address,
                            bucket_index=bucket_index,
                            deposit=wad_to_decimal(info[0]),
                            block_number=block_number,
                            block_datetime=self._block_datetimes[block_number],
                        )
                    except IntegrityError:
                        log.exception("Duplicated wallet bucket state")

                # handle bucket state
                bucket_info = results[f"{pool_address}:{bucket_index}"]
                try:
                    self._chain.bucket_state.objects.create(
                        pool_address=pool_address,
                        bucket_index=bucket_index,
                        bucket_price=wad_to_decimal(bucket_info[0]),
                        exchange_rate=wad_to_decimal(bucket_info[5]),
                        collateral=wad_to_decimal(bucket_info[2]),
                        deposit=wad_to_decimal(bucket_info[1]),
                        lpb=wad_to_decimal(bucket_info[3]),
                        block_number=block_number,
                        block_datetime=self._block_datetimes[block_number],
                    )
                except IntegrityError:
                    log.exception("Duplicated bucket state")

                # handle bucket
                self._chain.bucket.objects.update_or_create(
                    pool_address=pool_address,
                    bucket_index=bucket_index,
                    defaults={
                        "bucket_price": wad_to_decimal(bucket_info[0]),
                        "exchange_rate": wad_to_decimal(bucket_info[5]),
                        "collateral": wad_to_decimal(bucket_info[2]),
                        "deposit": wad_to_decimal(bucket_info[1]),
                        "lpb": wad_to_decimal(bucket_info[3]),
                    },
                )

    def _fetch_supply_for_wallet(
        self, pool_address, updated_bucket_wallets, wallet_address, block_number
    ):
        if wallet_address in updated_bucket_wallets:
            sql = """
                SELECT
                    SUM(x.deposit) AS supply
                FROM (
                    SELECT DISTINCT ON (bucket_index)
                        deposit
                    FROM
                        {wallet_bucket_state_table}
                    WHERE
                        pool_address = %s AND wallet_address = %s AND block_number <= %s
                    ORDER BY
                        bucket_index, block_number DESC
                ) x
            """.format(
                wallet_bucket_state_table=self._chain.wallet_bucket_state._meta.db_table
            )
            with connection.cursor() as cursor:
                cursor.execute(sql, [pool_address, wallet_address, block_number])
                data = fetch_one(cursor)
                self._wallet_supply[wallet_address] = data["supply"]
        elif wallet_address not in self._wallet_supply:
            with contextlib.suppress(self._chain.current_wallet_position.DoesNotExist):
                self._wallet_supply[
                    wallet_address
                ] = self._chain.current_wallet_position.objects.get(
                    pool_address=pool_address, wallet_address=wallet_address
                ).supply

        return self._wallet_supply[wallet_address]

    def _save_wallet_positions(self, block_number, to_update, results):
        # NOTE: this function must be called after the _save_buckets, otherwise supply
        # will not be updated correctly

        for pool_address, data in to_update.items():
            # Get a list of wallets that had buckets updated in this block, so we can
            # update the supply on the position itself
            updated_bucket_wallets = set()
            for bucket_wallets in data["buckets"].values():
                updated_bucket_wallets.update(bucket_wallets)

            inflator = wad_to_decimal(results[f"{pool_address}:inflatorInfo"][0])
            lup = wad_to_decimal(results[f"{pool_address}:pricesInfo"][4])

            for wallet_address in data["wallets"]:
                data = results[f"{pool_address}:{wallet_address}"]
                t0debt = wad_to_decimal(data[0])
                collateral = wad_to_decimal(data[1])

                supply = self._fetch_supply_for_wallet(
                    pool_address, updated_bucket_wallets, wallet_address, block_number
                )

                debt = round(t0debt * inflator)

                wallet_data = {
                    "supply": supply,
                    "collateral": collateral,
                    "t0debt": t0debt,
                    "debt": debt,
                    "block_number": block_number,
                    "datetime": self._block_datetimes[block_number],
                }

                (
                    current_position,
                    _,
                ) = self._chain.current_wallet_position.objects.update_or_create(
                    wallet_address=wallet_address,
                    pool_address=pool_address,
                    defaults=wallet_data,
                )

                self._chain.wallet_position.objects.create(
                    pool_address=pool_address,
                    wallet_address=wallet_address,
                    lup=lup,
                    pending_inflator=inflator,
                    in_liquidation=current_position.in_liquidation,
                    **wallet_data,
                )

                try:
                    wallet = self._chain.wallet.objects.get(address=wallet_address)
                except self._chain.wallet.DoesNotExist:
                    self._chain.wallet.objects.create(
                        address=wallet_address,
                        first_activity=self._block_datetimes[block_number],
                        last_activity=self._block_datetimes[block_number],
                        eoa=self._chain.get_eoa(wallet_address),
                    )
                else:
                    wallet.last_activity = self._block_datetimes[block_number]
                    wallet.save(update_fields=["last_activity"])

    def _save_wallets_and_buckets(self):
        for block_number, pool_data in sorted(self._data_to_update.items()):
            log.debug("_save_wallets_and_buckets processing: {}".format(block_number))
            calls = []
            for pool_address, data in pool_data.items():
                # Calls for wallets
                for wallet_address in data["wallets"]:
                    calls.append(
                        (
                            pool_address,
                            [
                                "borrowerInfo(address)((uint256,uint256,uint256))",
                                wallet_address,
                            ],
                            [f"{pool_address}:{wallet_address}", None],
                        )
                    )

                # Calls for buckets
                for bucket_index, bucket_wallets in data["buckets"].items():
                    calls.append(
                        (
                            self._chain.pool_info_address,
                            [
                                "bucketInfo(address,uint256)"
                                "((uint256,uint256,uint256,uint256,uint256,uint256))",
                                pool_address,
                                bucket_index,
                            ],
                            [f"{pool_address}:{bucket_index}", None],
                        )
                    )

                    for wallet_address in bucket_wallets:
                        calls.append(
                            (
                                pool_address,
                                [
                                    "lenderInfo(uint256,address)((uint256,uint256))",
                                    bucket_index,
                                    wallet_address,
                                ],
                                [
                                    f"{pool_address}:{bucket_index}:{wallet_address}",
                                    None,
                                ],
                            )
                        )

                # Call for inflator
                calls.append(
                    (
                        pool_address,
                        ["inflatorInfo()((uint256,uint256))"],
                        [f"{pool_address}:inflatorInfo", None],
                    )
                )
                # Call for lup
                calls.append(
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
                )

            results = self._chain.multicall(calls, block_identifier=block_number)

            self._save_buckets(block_number, pool_data, results)
            self._save_wallet_positions(block_number, pool_data, results)

    def _create_notifications(self, event):
        match event.name:
            case "AddQuoteToken":
                if event.quote_token_price:
                    amount = wad_to_decimal(event.data["amount"])
                    amount_usd = amount * event.quote_token_price
                    if amount_usd >= Decimal("1000000"):
                        self._chain.notification.objects.get_or_create(
                            type=event.name,
                            key=event.order_index,
                            pool_address=event.pool_address,
                            defaults={
                                "data": {
                                    "amount": amount,
                                    "quote_token_price": event.quote_token_price,
                                    "amount_usd": amount_usd,
                                    "lp_awarded": wad_to_decimal(
                                        event.data["lpAwarded"]
                                    ),
                                    "wallet_address": event.data["lender"].lower(),
                                },
                                "datetime": event.block_datetime,
                            },
                        )
            case "DrawDebt":
                if event.quote_token_price:
                    amount = wad_to_decimal(event.data["amountBorrowed"])
                    amount_usd = amount * event.quote_token_price
                    if amount_usd >= Decimal("1000000"):
                        self._chain.notification.objects.get_or_create(
                            type=event.name,
                            key=event.order_index,
                            pool_address=event.pool_address,
                            defaults={
                                "data": {
                                    "amount": amount,
                                    "quote_token_price": event.quote_token_price,
                                    "amount_usd": amount_usd,
                                    "collateral": wad_to_decimal(
                                        event.data["collateralPledged"]
                                    ),
                                    "wallet_address": event.data["borrower"].lower(),
                                },
                                "datetime": event.block_datetime,
                            },
                        )
            case "AddCollateral":
                self._chain.notification.objects.get_or_create(
                    type=event.name,
                    key=event.order_index,
                    pool_address=event.pool_address,
                    defaults={
                        "data": {
                            "actor": event.data["actor"],
                            "index": event.data["index"],
                            "amount": wad_to_decimal(event.data["amount"]),
                            "lpAwarded": wad_to_decimal(event.data["lpAwarded"]),
                        },
                        "datetime": event.block_datetime,
                    },
                )
            case "Kick":
                self._chain.notification.objects.get_or_create(
                    type=event.name,
                    key=event.order_index,
                    pool_address=event.pool_address,
                    defaults={
                        "data": {
                            "bond": wad_to_decimal(event.data["bond"]),
                            "debt": wad_to_decimal(event.data["debt"]),
                            "borrower": event.data["borrower"],
                            "collateral": wad_to_decimal(event.data["collateral"]),
                        },
                        "datetime": event.block_datetime,
                    },
                )
            case "AuctionSettle":
                self._chain.notification.objects.get_or_create(
                    type=event.name,
                    key=event.order_index,
                    pool_address=event.pool_address,
                    defaults={
                        "data": {
                            "borrower": event.data["borrower"],
                            "collateral": wad_to_decimal(event.data["collateral"]),
                        },
                        "datetime": event.block_datetime,
                    },
                )

    def _process_auctions(self, event):
        match event.name:
            case "Kick":
                process_kick_event(self._chain, event)
            case "Take":
                process_take_event(self._chain, event)
            case "BucketTake":
                process_bucket_take_event(self._chain, event)
            case "Settle":
                process_settle_event(self._chain, event)
            case "AuctionSettle" | "AuctionNFTSettle":
                process_auction_settle_event(self._chain, event)

    def _process_reserve_auctions(self, event):
        match event.name:
            case "KickReserveAuction":
                process_kick_reserve_auction_event(self._chain, event)
            case "ReserveAuction":
                process_reserve_auction_event(self._chain, event)

    def _post_process_events(self, processed_pool_events):
        for pool_address, data in processed_pool_events.items():
            events = self._chain.pool_event.objects.filter(
                pool_address=pool_address,
                order_index__gte=data["from"],
                order_index__lte=data["to"],
            ).order_by("order_index")

            for event in events:
                self._create_notifications(event)
                self._process_auctions(event)
                self._process_reserve_auctions(event)

            # Update pools last_block_number to the last event block number
            # so on the next run we start from that block number onwards
            if event:
                self._chain.pool.objects.filter(address=pool_address).update(
                    last_block_number=event.block_number
                )

    def process_all_events(self):
        pools = self._chain.pool.objects.all().values("address", "last_block_number")

        processed_pool_events = {}
        for pool in pools:
            filters = {}
            # Figure out which last block number to use. We decide here which one to use
            # either from pool or from position, as it's possible that an error happens
            # and on the pool it's not updated to the last block, so in that case
            # get it from current position
            current_position = (
                self._chain.current_wallet_position.objects.filter(
                    pool_address=pool["address"]
                )
                .order_by("-datetime")
                .first()
            )
            current_pos_last_block = 0
            if current_position:
                current_pos_last_block = current_position.block_number

            last_block_num = max(pool["last_block_number"] or 0, current_pos_last_block)
            if last_block_num:
                filters["block_number__gt"] = last_block_num

            events = list(
                self._chain.pool_event.objects.filter(
                    pool_address=pool["address"], **filters
                ).order_by("order_index")
            )

            if not events:
                log.debug("No new events for pool {}".format(pool["address"]))
                continue

            processed_pool_events[pool["address"]] = {
                "from": events[0].order_index,
                "to": events[-1].order_index,
            }

            self._build_wallets_and_buckets_to_update(events)

        self._save_wallets_and_buckets()

        self._post_process_events(processed_pool_events)
