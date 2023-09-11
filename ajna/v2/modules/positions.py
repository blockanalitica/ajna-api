import contextlib
import logging
from collections import defaultdict
from decimal import Decimal

from django.db import IntegrityError, connection

from ajna.utils.db import fetch_one
from ajna.utils.wad import wad_to_decimal

log = logging.getLogger(__name__)


class EventProcessor:
    def __init__(self, chain, pool_address):
        self._chain = chain
        self._pool_address = pool_address

        self._block_datetimes = {}

        self._wallet_supply = defaultdict(Decimal)

    def _get_data_to_update_from_events(self, events):
        data_to_update = defaultdict(
            lambda: {
                "wallets": set(),
                "buckets": defaultdict(set),
            }
        )

        for event in events:
            self._block_datetimes[event.block_number] = event.block_datetime

            if event.wallet_addresses:
                data_to_update[event.block_number]["wallets"].update(
                    event.wallet_addresses
                )
            match event.name:
                case "AddQuoteToken" | "RemoveQuoteToken":
                    data_to_update[event.block_number]["buckets"][
                        event.data["index"]
                    ].add(event.wallet_addresses[0])

                case "MoveQuoteToken":
                    data_to_update[event.block_number]["buckets"][
                        event.data["from"]
                    ].add(event.wallet_addresses[0])
                    data_to_update[event.block_number]["buckets"][event.data["to"]].add(
                        event.wallet_addresses[0]
                    )

                case "AddCollateral" | "RemoveCollateral":
                    data_to_update[event.block_number]["buckets"][
                        event.data["index"]
                    ].add(event.wallet_addresses[0])

                case "BucketTake":
                    bucket_index = event.data["index"]
                    wallets = set(
                        self._chain.wallet_bucket_state.objects.filter(
                            pool_address=self._pool_address,
                            bucket_index=bucket_index,
                        ).values_list("wallet_address", flat=True)
                    )

                    data_to_update[event.block_number]["buckets"][bucket_index].update(
                        wallets
                    )
                case "TransferLP":
                    for bucket_index in event.data["indexes"]:
                        data_to_update[event.block_number]["buckets"][
                            bucket_index
                        ].update(event.wallet_addresses)

                case "IncreaseLPAllowance":
                    for bucket_index in event.data["indexes"]:
                        data_to_update[event.block_number]["buckets"][
                            bucket_index
                        ].update(event.wallet_addresses)

        return data_to_update

    def _save_buckets(self, block_number, buckets, results):
        for bucket_index, wallet_addresses in buckets.items():
            # Handle wallet buckets
            for wallet_address in wallet_addresses:
                info = results[f"{bucket_index}:{wallet_address}"]
                try:
                    self._chain.wallet_bucket_state.objects.create(
                        wallet_address=wallet_address,
                        pool_address=self._pool_address,
                        bucket_index=bucket_index,
                        deposit=wad_to_decimal(info[0]),
                        block_number=block_number,
                        block_datetime=self._block_datetimes[block_number],
                    )
                except IntegrityError:
                    log.exception("Duplicated wallet bucket state")

            # handle bucket state
            bucket_info = results[f"{bucket_index}"]
            try:
                self._chain.bucket_state.objects.create(
                    pool_address=self._pool_address,
                    bucket_index=bucket_index,
                    bucket_price=wad_to_decimal(bucket_info[0]),
                    exchange_rate=wad_to_decimal(bucket_info[4]),
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
                pool_address=self._pool_address,
                bucket_index=bucket_index,
                defaults={
                    "bucket_price": wad_to_decimal(bucket_info[0]),
                    "exchange_rate": wad_to_decimal(bucket_info[4]),
                    "collateral": wad_to_decimal(bucket_info[1]),
                    "deposit": wad_to_decimal(bucket_info[0]),
                    "lpb": wad_to_decimal(bucket_info[3]),
                },
            )

    def _fetch_supply_for_wallet(
        self, updated_bucket_wallets, wallet_address, block_number
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
                cursor.execute(sql, [self._pool_address, wallet_address, block_number])
                data = fetch_one(cursor)
                self._wallet_supply[wallet_address] = data["supply"]
        elif wallet_address not in self._wallet_supply:
            with contextlib.suppress(self._chain.current_wallet_position.DoesNotExist):
                self._wallet_supply[
                    wallet_address
                ] = self._chain.current_wallet_position.objects.get(
                    pool_address=self._pool_address, wallet_address=wallet_address
                ).supply

        return self._wallet_supply[wallet_address]

    def _save_wallet_positions(self, block_number, to_update, results):
        # NOTE: this function must be called after the _save_buckets, otherwise supply
        # will not be updated correctly

        # Get a list of wallets that had buckets updated in this block, so we can
        # update the supply on the position itself
        updated_bucket_wallets = set()
        for bucket_wallets in to_update["buckets"].values():
            updated_bucket_wallets.update(bucket_wallets)

        inflator = wad_to_decimal(results["inflatorInfo"][0])
        for wallet_address in to_update["wallets"]:
            data = results[wallet_address]
            t0debt = wad_to_decimal(data[0])
            collateral = wad_to_decimal(data[1])

            supply = self._fetch_supply_for_wallet(
                updated_bucket_wallets, wallet_address, block_number
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

            self._chain.wallet_position.objects.create(
                pool_address=self._pool_address,
                wallet_address=wallet_address,
                **wallet_data,
            )

            self._chain.current_wallet_position.objects.update_or_create(
                wallet_address=wallet_address,
                pool_address=self._pool_address,
                defaults=wallet_data,
            )

    def _save_wallets_and_buckets(self, events):
        data_to_update = self._get_data_to_update_from_events(events)
        for block_number, data in data_to_update.items():
            log.debug("_save_wallets_and_buckets processing: {}".format(block_number))

            calls = []
            # Calls for wallets
            for wallet_address in data["wallets"]:
                calls.append(
                    (
                        self._pool_address,
                        [
                            "borrowerInfo(address)((uint256,uint256,uint256))",
                            wallet_address,
                        ],
                        [f"{wallet_address}", None],
                    )
                )

            # Calls for buckets
            for bucket_index, bucket_wallets in data["buckets"].items():
                calls.append(
                    (
                        self._pool_address,
                        [
                            "bucketInfo(uint256)((uint256,uint256,uint256,uint256,uint256))",
                            bucket_index,
                        ],
                        [f"{bucket_index}", None],
                    )
                )

                for wallet_address in bucket_wallets:
                    calls.append(
                        (
                            self._pool_address,
                            [
                                "lenderInfo(uint256,address)((uint256,uint256))",
                                bucket_index,
                                wallet_address,
                            ],
                            [f"{bucket_index}:{wallet_address}", None],
                        )
                    )

            # Call for inflator
            calls.append(
                (
                    self._pool_address,
                    ["inflatorInfo()((uint256,uint256))"],
                    ["inflatorInfo", None],
                )
            )

            results = self._chain.multicall(calls, block_identifier=block_number)

            self._save_buckets(block_number, data["buckets"], results)
            self._save_wallet_positions(block_number, data, results)

    def process_events(self, from_block=None):
        filters = {}
        if from_block:
            filters["block_number__gt"] = from_block
        else:
            last_position = (
                self._chain.current_wallet_position.objects.filter(
                    pool_address=self._pool_address
                )
                .order_by("-block_number")
                .first()
            )
            if last_position:
                filters["block_number__gt"] = last_position.block_number

        events = (
            self._chain.pool_event.objects.filter(
                pool_address=self._pool_address, **filters
            )
            .exclude(name="UpdateInterestRate")
            .order_by("order_index")
        )

        if not events:
            log.debug("No events")
            return

        self._save_wallets_and_buckets(events)
