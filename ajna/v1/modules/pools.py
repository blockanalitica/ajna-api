from datetime import datetime
from decimal import Decimal

from django.db import connection

from ajna.sources.defillama import get_current_prices
from ajna.utils.db import fetch_all
from ajna.utils.utils import (
    date_to_timestamp,
    datetime_to_full_hour,
    datetime_to_next_full_hour,
)


def get_pools_chain_data(chain, pool_addresses):
    calls = []

    for pool_address in pool_addresses:
        calls.append(
            (
                chain.pool_info_address,
                [
                    "poolLoansInfo(address)((uint256,uint256,address,uint256,uint256))",
                    pool_address,
                ],
                [f"{pool_address}:loansInfo", None],
            )
        )
        calls.append(
            (
                chain.pool_info_address,
                [
                    "poolPricesInfo(address)((uint256,uint256,uint256,uint256,uint256,uint256))",
                    pool_address,
                ],
                [f"{pool_address}:pricesInfo", None],
            )
        )

    data = chain.call_multicall(calls)

    pools_data = {}
    for pool_address in pool_addresses:
        loans_info = data[f"{pool_address}:loansInfo"]
        prices_info = data[f"{pool_address}:pricesInfo"]
        pools_data[pool_address] = {
            "pending_inflator": loans_info[3] / 10**18,
            "hpb_index": prices_info[1],
            "htp_index": prices_info[3],
            "lup_index": prices_info[5],
        }
    return pools_data


def fetch_pools_data(chain, subgraph, models):
    fetch_and_save_pool_data(
        chain, subgraph, models.pool, models.token, models.pool_snapshot
    )
    fetch_and_save_buckets(subgraph, models.bucket)


def fetch_and_save_pool_data(
    chain, subgraph, pool_model, token_model, pool_snapshot_model
):
    """
    Fetches pool data from the Subgraph and saves it to the database.

    This function fetches pool data from the Subgraph, updates or creates
    corresponding Pool instances in the database, and optionally creates
    PoolSnapshot instances for each pool. If a new pool is created, it will
    also attempt to create new Token instances if they don't already exist.

    Args:
        pool_model (models.Model): The Pool model class.
        token_model (models.Model): The Token model class.
        pool_snapshot_model (models.Model): The PoolSnapshot model class.
        snapshot (bool, optional): Whether to create PoolSnapshot instances. Defaults to True.

    Usage:
        fetch_and_save_pool_data(Pool, Token, PoolSnapshot)
    """

    pools_data = subgraph.pools()
    pool_addresses = [pool_data["id"] for pool_data in pools_data]
    chain_pools_data = get_pools_chain_data(chain, pool_addresses)

    dt = datetime_to_full_hour(datetime.now())

    for pool_data in pools_data:
        collateral_token = pool_data["collateralToken"]
        quote_token = pool_data["quoteToken"]

        chain_pool_data = chain_pools_data.get(pool_data["id"], {})

        pool_size = Decimal(pool_data["poolSize"])
        t0debt = Decimal(pool_data["t0debt"])
        pending_inflator = Decimal(chain_pool_data.get("pending_inflator", 1))
        debt = t0debt * pending_inflator

        utilization = Decimal("0")
        if pool_size > 0:
            utilization = debt / pool_size

        # If lup is max price, set it to 0 as max price means there are no loans
        lup = Decimal(pool_data["lup"])
        # Max lup is 1004968987.6065123
        if lup > Decimal("1004968987"):
            lup = Decimal("0")

        pool_defaults = {
            "created_at_block_number": pool_data["createdAtBlockNumber"],
            "created_at_timestamp": pool_data["createdAtTimestamp"],
            "collateral_token_address": collateral_token["id"],
            "quote_token_address": quote_token["id"],
            "pool_size": pool_size,
            "debt": debt,
            "t0debt": pool_data["t0debt"],
            "inflator": pool_data["inflator"],
            "pending_inflator": pending_inflator,
            "borrow_rate": pool_data["borrowRate"],
            "lend_rate": pool_data["lendRate"],
            "borrow_fee_rate": pool_data["borrowFeeRate"],
            "deposit_fee_rate": pool_data["depositFeeRate"],
            "pledged_collateral": pool_data["pledgedCollateral"],
            "total_interest_earned": pool_data["totalInterestEarned"],
            "tx_count": pool_data["txCount"],
            "loans_count": pool_data["loansCount"],
            "max_borrower": pool_data["maxBorrower"],
            "hpb": pool_data["hpb"],
            "hpb_index": chain_pool_data.get("hpb_index", pool_data["hpbIndex"]),
            "htp": pool_data["htp"],
            "htp_index": chain_pool_data.get("htp_index", pool_data["htpIndex"]),
            "lup": lup,
            "lup_index": chain_pool_data.get("lup_index", pool_data["lupIndex"]),
            "momp": pool_data["momp"],
            "reserves": pool_data["reserves"],
            "claimable_reserves": pool_data["claimableReserves"],
            "claimable_reserves_remaining": pool_data["claimableReservesRemaining"],
            "burn_epoch": pool_data["burnEpoch"],
            "total_ajna_burned": pool_data["totalAjnaBurned"],
            "min_debt_amount": pool_data["minDebtAmount"],
            "utilization": utilization,
            "actual_utilization": pool_data["actualUtilization"],
            "target_utilization": pool_data["targetUtilization"],
            "total_bond_escrowed": pool_data["totalBondEscrowed"],
            "quote_token_balance": pool_data["quoteTokenBalance"],
            "collateral_token_balance": pool_data["collateralBalance"],
            "datetime": datetime.now(),
        }
        _, created = pool_model.objects.update_or_create(
            address=pool_data["id"], defaults=pool_defaults
        )
        if created:
            _, collateral_created = token_model.objects.get_or_create(
                underlying_address=collateral_token["id"],
                defaults={
                    "symbol": collateral_token["symbol"],
                    "name": collateral_token["name"],
                    "decimals": collateral_token["decimals"],
                    "is_erc721": collateral_token["isERC721"],
                },
            )

            _, quote_created = token_model.objects.get_or_create(
                underlying_address=quote_token["id"],
                defaults={
                    "symbol": quote_token["symbol"],
                    "name": quote_token["name"],
                    "decimals": quote_token["decimals"],
                    "is_erc721": quote_token["isERC721"],
                },
            )

            if collateral_created or quote_created:
                chain.celery_tasks.fetch_market_price_task.delay()

        # Remove fields specific to the Pool model to avoid saving them in the PoolSnapshot model
        pool_defaults.pop("created_at_block_number")
        pool_defaults.pop("created_at_timestamp")
        pool_defaults.pop("datetime")

        # Add PoolSnapshot specific fields
        try:
            collateral_token = token_model.objects.get(
                underlying_address=pool_defaults["collateral_token_address"]
            )
        except token_model.DoesNotExist:
            pass
        else:
            pool_defaults["collateral_token_price"] = collateral_token.underlying_price

        try:
            quote_token = token_model.objects.get(
                underlying_address=pool_defaults["quote_token_address"]
            )
        except token_model.DoesNotExist:
            pass
        else:
            pool_defaults["quote_token_price"] = quote_token.underlying_price

        collateralization = None
        if (
            Decimal(pool_defaults["t0debt"]) > 0
            and Decimal(pool_defaults["pending_inflator"]) > 0
            and quote_token.underlying_price
            and collateral_token.underlying_price
        ):
            collateralization = (
                Decimal(pool_defaults["pledged_collateral"])
                * collateral_token.underlying_price
            ) / (
                Decimal(pool_defaults["t0debt"])
                * Decimal(pool_defaults["pending_inflator"])
                * quote_token.underlying_price
            )

        pool_defaults["collateralization"] = collateralization

        pool_snapshot_model.objects.update_or_create(
            address=pool_data["id"],
            datetime=datetime_to_next_full_hour(dt),
            defaults=pool_defaults,
        )


def fetch_and_save_buckets(subgraph, bucket_model):
    """
    Fetches bucket data from the Subgraph and saves it to the Bucket model.

    This function fetches bucket data from the Subgraph, then creates and
    saves corresponding Bucket instances in the database. The buckets are
    identified by their `bucket_index` and `pool_address` attributes.

    Args:
        bucket_model (models.Model): The Bucket model class.

    Usage:
        fetch_and_save_buckets(Bucket)
    """
    buckets_data = subgraph.buckets()

    for bucket_data in buckets_data:
        bucket_index = bucket_data["bucketIndex"]
        pool_address = bucket_data["poolAddress"]

        bucket_model.objects.update_or_create(
            bucket_index=bucket_index,
            pool_address=pool_address,
            defaults={
                "bucket_price": bucket_data["bucketPrice"],
                "exchange_rate": bucket_data["exchangeRate"],
                "collateral": bucket_data["collateral"],
                "deposit": bucket_data["deposit"],
                "lpb": bucket_data["lpb"],
            },
        )


def update_token_prices(token_model, price_feed_model, network="ethereum"):
    """
    Updates the underlying_price field for all Token instances in the database.

    This function retrieves all the underlying addresses of the tokens, fetches the
    current prices for those addresses, and then updates the corresponding token
    instances with the new prices.

    Args:
        token_model (models.Model): The Token model class.

    Usage:
        update_token_prices(Token)
    """
    if network == "goerli":
        MAPPING_TO_ETHEREUM = {
            "0x9c09fe6b19174d838cae2c4fb5a4a311c4008441": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  # TWETH
            "0x10aa0cf12aab305bd77ad8f76c037e048b12513b": "0x6b175474e89094c44da98b954eedeac495271d0f",  # TDAI
            "0x7ccf0411c7932b99fc3704d68575250f032e3bb7": "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",  # WBTC
            "0x6fb5ef893d44f4f88026430d82d4ef269543cb23": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",  # USDC
            "0xb4fbf271143f4fbf7b91a5ded31805e42b2208d6": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  # WETH
            "0x11fe4b6ae13d2a6055c8d9cf65c55bac32b5d844": "0x6b175474e89094c44da98b954eedeac495271d0f",  # DAI
            "0x6320cd32aa674d2898a68ec82e869385fc5f7e2f": "0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0",  # wstETH
            "0x62bc478ffc429161115a6e4090f819ce5c50a5d9": "0xae78736cd615f374d3085123a210448e74fc6393",  # rETH
            "0xdf1742fe5b0bfc12331d8eaec6b478dfdbd31464": "0x6b175474e89094c44da98b954eedeac495271d0f",  # DAI
            "0x4f1ef08f55fbc2eeddd79ff820357e8d25e49793": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",  # TUSDC
        }
        MAPPING_TO_GOERLI = {
            "0x6b175474e89094c44da98b954eedeac495271d0f": [
                "0x10aa0cf12aab305bd77ad8f76c037e048b12513b",
                "0x11fe4b6ae13d2a6055c8d9cf65c55bac32b5d844",
                "0xdf1742fe5b0bfc12331d8eaec6b478dfdbd31464",
            ],  # DAI
            "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599": [
                "0x7ccf0411c7932b99fc3704d68575250f032e3bb7"
            ],  # WBTC
            "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": [
                "0x6fb5ef893d44f4f88026430d82d4ef269543cb23",
                "0x4f1ef08f55fbc2eeddd79ff820357e8d25e49793",
            ],  # USDC
            "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": [
                "0xb4fbf271143f4fbf7b91a5ded31805e42b2208d6",
                "0x9c09fe6b19174d838cae2c4fb5a4a311c4008441",
            ],  # WETH
            "0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0": [
                "0x6320cd32aa674d2898a68ec82e869385fc5f7e2f"
            ],  # wstETH
            "0xae78736cd615f374d3085123a210448e74fc6393": [
                "0x62bc478ffc429161115a6e4090f819ce5c50a5d9"
            ],  # rETH
        }
        underlying_addresses = token_model.objects.all().values_list(
            "underlying_address", flat=True
        )
        addresses = []
        for a in underlying_addresses:
            addresses.append(MAPPING_TO_ETHEREUM.get(a, a))
        prices_mapping = get_current_prices(addresses)
        for key, values in prices_mapping.items():
            _, underlying_address = key.split(":")
            underlying_addresses = MAPPING_TO_GOERLI.get(
                underlying_address, [underlying_address]
            )
            for underlying_address in underlying_addresses:
                price = Decimal(str(values["price"]))
                token_model.objects.filter(
                    underlying_address=underlying_address
                ).update(underlying_price=price)
                try:
                    price_feed = price_feed_model.objects.filter(
                        underlying_address=underlying_address
                    ).latest()
                except price_feed_model.DoesNotExist:
                    price_feed = None
                if price_feed is None or price_feed.price != price:
                    price_feed_model.objects.create(
                        underlying_address=underlying_address,
                        price=price,
                        datetime=datetime.now(),
                        timestamp=datetime.now().timestamp(),
                    )

    else:
        underlying_addresses = token_model.objects.all().values_list(
            "underlying_address", flat=True
        )
        prices_mapping = get_current_prices(underlying_addresses)
        for key, values in prices_mapping.items():
            _, underlying_address = key.split(":")
            price = Decimal(str(values["price"]))
            token_model.objects.filter(underlying_address=underlying_address).update(
                underlying_price=price
            )
            try:
                price_feed = price_feed_model.objects.filter(
                    underlying_address=underlying_address
                ).latest()
            except price_feed_model.DoesNotExist:
                price_feed = None
            if price_feed is None or price_feed.price != price:
                price_feed_model.objects.create(
                    underlying_address=underlying_address,
                    price=price,
                    datetime=datetime.now(),
                    timestamp=datetime.now().timestamp(),
                )


def calculate_pool_volume_for_date(models, for_date):
    ts_from = date_to_timestamp(for_date)
    ts_to = int(
        datetime(
            year=for_date.year,
            month=for_date.month,
            day=for_date.day,
            hour=23,
            minute=59,
            second=59,
        ).timestamp()
    )

    sql = """
        SELECT
              pool_address
            , SUM(amount) AS total_amount
        FROM (
            SELECT
                  pool_address
                , amount * price AS amount
                , block_timestamp
            FROM {add_collateral_table}
            WHERE block_timestamp >= %s AND block_timestamp <= %s
            UNION ALL
            SELECT
                 pool_address
                , amount * price AS amount
                , block_timestamp
            FROM {remove_collateral_table}
            WHERE block_timestamp >= %s AND block_timestamp <= %s
            UNION ALL
            SELECT
                  pool_address
                , amount * price AS amount
                , block_timestamp
            FROM {add_quote_token_table}
            WHERE block_timestamp >= %s AND block_timestamp <= %s
            UNION ALL
            SELECT
                pool_address
                , amount * price AS amount
                , block_timestamp
            FROM {remove_quote_token_table}
            WHERE block_timestamp >= %s AND block_timestamp <= %s
            UNION ALL
            SELECT
                  pool_address
                , (amount_borrowed * quote_token_price
                   + collateral_pledged * collateral_token_price) AS amount
                , block_timestamp
            FROM {draw_debt_table}
            WHERE block_timestamp >= %s AND block_timestamp <= %s
            UNION ALL
            SELECT
                  pool_address
                , (quote_repaid * quote_token_price
                   + collateral_pulled * collateral_token_price) AS amount
                , block_timestamp
            FROM {repay_debt_table}
            WHERE block_timestamp >= %s AND block_timestamp <= %s
        ) AS subquery
        GROUP BY pool_address
    """.format(
        add_collateral_table=models.add_collateral._meta.db_table,
        remove_collateral_table=models.remove_collateral._meta.db_table,
        add_quote_token_table=models.add_quote_token._meta.db_table,
        remove_quote_token_table=models.remove_quote_token._meta.db_table,
        draw_debt_table=models.draw_debt._meta.db_table,
        repay_debt_table=models.repay_debt._meta.db_table,
    )

    sql_vars = [ts_from, ts_to] * 6
    with connection.cursor() as cursor:
        cursor.execute(sql, sql_vars)
        volumes = fetch_all(cursor)

    for volume in volumes:
        if volume["total_amount"]:
            models.pool_volume_snapshot.objects.update_or_create(
                pool_address=volume["pool_address"],
                date=for_date,
                defaults={
                    "amount": volume["total_amount"],
                },
            )
