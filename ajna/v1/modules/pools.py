from datetime import datetime
from decimal import Decimal

from django.db import connection

from ajna.utils.db import fetch_all
from ajna.utils.utils import (
    date_to_timestamp,
    datetime_to_full_hour,
    datetime_to_next_full_hour,
    wad_to_decimal,
)


def get_pools_chain_data(chain, pool_addresses, block_number=None):
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
        calls.append(
            (
                pool_address,
                ["interestRateInfo()((uint256,uint256))"],
                [f"{pool_address}:interestRateInfo", None],
            ),
        )
        calls.append(
            (
                pool_address,
                ["debtInfo()((uint256,uint256,uint256,uint256))"],
                [f"{pool_address}:debtInfo", None],
            ),
        )
        calls.append(
            (
                chain.pool_info_address,
                [
                    "lenderInterestMargin(address)(uint256)",
                    pool_address,
                ],
                [f"{pool_address}:lenderInterestMargin", None],
            )
        )

    data = chain.multicall(calls, block_identifier=block_number)

    pools_data = {}
    for pool_address in pool_addresses:
        loans_info = data[f"{pool_address}:loansInfo"]
        prices_info = data[f"{pool_address}:pricesInfo"]
        interest_rate_info = data[f"{pool_address}:interestRateInfo"]
        debt_info = data[f"{pool_address}:debtInfo"]
        lim = data[f"{pool_address}:lenderInterestMargin"]

        pools_data[pool_address] = {
            "pending_inflator": wad_to_decimal(loans_info[3]),
            "hpb_index": prices_info[1],
            "htp_index": prices_info[3],
            "lup_index": prices_info[5],
            "borrow_rate": wad_to_decimal(interest_rate_info[0]),
            "lender_interest_margin": wad_to_decimal(lim),
            "pending_debt": wad_to_decimal(debt_info[0]),
        }

    # _calculate_lend_rates mutates pools_data and adds keys to it
    _calculate_lend_rates(chain, pools_data, block_number)

    return pools_data


def _calculate_lend_rates(chain, pools_data, block_number=None):
    """
    NOTE: This function mutates pools_data dictionary that is passed in this function
    as parameter!
    """
    calls = []
    for pool_address, pool_data in pools_data.items():
        calls.append(
            (
                pool_address,
                [
                    "depositUpToIndex(uint256)(uint256)",
                    max(pool_data["lup_index"], pool_data["htp_index"]),
                ],
                [pool_address, None],
            )
        )

    deposit_data = chain.multicall(calls, block_identifier=block_number)

    for pool_address, pool_data in pools_data.items():
        meaningful_deposit = wad_to_decimal(deposit_data[pool_address])

        utilization = None
        lend_rate = Decimal("0")
        if meaningful_deposit:
            utilization = pool_data["pending_debt"] / meaningful_deposit
            lend_rate = (
                pool_data["borrow_rate"]
                * pool_data["lender_interest_margin"]
                * utilization
            )

        pool_data["current_meaningful_utilization"] = utilization
        pool_data["lend_rate"] = lend_rate


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

    pools_data = list(subgraph.pools())
    pool_addresses = [pool_data["id"] for pool_data in pools_data]
    chain_pools_data = get_pools_chain_data(chain, pool_addresses)

    dt = datetime_to_full_hour(datetime.now())

    for pool_data in pools_data:
        collateral_token = pool_data["collateralToken"]
        quote_token = pool_data["quoteToken"]

        chain_pool_data = chain_pools_data.get(pool_data["id"], {})

        pool_size = Decimal(pool_data["poolSize"])
        t0debt = Decimal(pool_data["t0debt"])
        pending_inflator = chain_pool_data.get("pending_inflator", Decimal("1"))
        debt = t0debt * pending_inflator

        utilization = Decimal("0")
        if pool_size > 0:
            utilization = min(debt / pool_size, Decimal("1"))

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
            "borrow_rate": chain_pool_data.get(
                "borrow_rate", Decimal(str(pool_data["borrowRate"]))
            ),
            "lend_rate": chain_pool_data.get(
                "lend_rate", Decimal(str(pool_data["lendRate"]))
            ),
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
            "current_meaningful_utilization": chain_pool_data[
                "current_meaningful_utilization"
            ],
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
