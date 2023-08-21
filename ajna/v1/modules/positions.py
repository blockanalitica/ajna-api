from collections import defaultdict
from datetime import datetime
from decimal import Decimal

from django.db import connection

from ajna.utils.db import fetch_all
from ajna.utils.wad import wad_to_decimal, round_ceil

POOL_BLOCK_DATA = defaultdict(dict)


def _get_pool_block_data(chain, pool_address, block_number):
    global POOL_BLOCK_DATA

    if block_number not in POOL_BLOCK_DATA[pool_address]:
        interest_rate_calls = [
            (
                pool_address,
                ["interestRateInfo()((uint256,uint256))"],
                ["interestRateInfo", None],
            ),
        ]
        # Get interestRateInfo from the previous block, because when drawDebt event
        # happens, immediately after the `UpdateInterestRate` is called changing
        # the borrow rate for the current block, but the drawDebt calculation happens
        # with the previous blocks borrow rate
        interest_rates = chain.call_multicall(
            interest_rate_calls, block_id=block_number - 1
        )

        inflator_info_calls = [
            (
                pool_address,
                ["inflatorInfo()((uint256,uint256))"],
                ["inflatorInfo", None],
            ),
        ]
        inflator_info = chain.call_multicall(inflator_info_calls, block_id=block_number)

        POOL_BLOCK_DATA[pool_address][block_number] = {
            "inflator": wad_to_decimal(inflator_info["inflatorInfo"][0]),
            "borrow_rate": wad_to_decimal(interest_rates["interestRateInfo"][0]),
        }

    return POOL_BLOCK_DATA[pool_address][block_number]


def _update_current_positions_block(current_position, event):
    # Only update block_number and datetime if event's block_number is greater
    # than the existing one as otherwise we might store the wrong block_number
    # since we're processing different events separately
    if event["block_number"] > current_position[event["pool_address"]]["block_number"]:
        current_position[event["pool_address"]]["block_number"] = event["block_number"]
        current_position[event["pool_address"]]["datetime"] = datetime.fromtimestamp(
            event["block_timestamp"]
        )


def _handle_debt_events(chain, wallet_address, from_block_number, curr_positions):
    # TODO: from_block_number
    sql = """
        SELECT
             dd.pool_address
           , dd.block_timestamp
           , dd.block_number
           , dd.amount_borrowed AS debt
           , dd.collateral_pledged AS collateral
        FROM {draw_debt_table} AS dd
        WHERE dd.borrower = %s

        UNION

        SELECT
              rd.pool_address
            , rd.block_timestamp
            , rd.block_number
            , rd.quote_repaid * -1 AS debt
            , rd.collateral_pulled * -1 AS collateral
        FROM {repay_debt_table} rd
        WHERE rd.borrower = %s
        ORDER BY block_number
    """.format(
        draw_debt_table=chain.draw_debt._meta.db_table,
        repay_debt_table=chain.repay_debt._meta.db_table,
    )
    with connection.cursor() as cursor:
        cursor.execute(sql, [wallet_address, wallet_address])
        events = fetch_all(cursor)

    for event in events:
        block_data = _get_pool_block_data(
            chain, event["pool_address"], event["block_number"]
        )

        # In contract they round t0debt to ceiling, while origination fee and others
        # below are rounded normally
        t0debt = round_ceil(event["debt"] / block_data["inflator"])
        if event["debt"] > 0:
            origination_fee = round(
                max(round(block_data["borrow_rate"] / 52, 18), Decimal("0.0005"))
                * t0debt,
                18,
            )

            t0debt += origination_fee

        curr_positions[event["pool_address"]]["debt"] += event["debt"]
        curr_positions[event["pool_address"]]["t0debt"] += t0debt
        curr_positions[event["pool_address"]]["collateral"] += event["collateral"]
        _update_current_positions_block(curr_positions, event)


def _handle_quote_token_events(
    chain, wallet_address, from_block_number, curr_positions
):
    # TODO: from_block_number
    sql = """
        SELECT
              aqt.pool_address
            , 'add' AS type
            , aqt.block_timestamp
            , aqt.block_number
            , aqt.bucket_index
            , CAST(NULL AS numeric) AS bucket_index_from
            , CAST(NULL AS numeric) AS bucket_index_to
            , aqt.amount
        FROM {add_quote_token_table} AS aqt
        WHERE aqt.lender = %s

        UNION

        SELECT
              rqt.pool_address
            , 'remove' AS type
            , rqt.block_timestamp
            , rqt.block_number
            , rqt.bucket_index
            , CAST(NULL AS numeric) AS bucket_index_from
            , CAST(NULL AS numeric) AS bucket_index_to
            , rqt.amount
        FROM {remove_quote_token_table} rqt
        WHERE rqt.lender = %s

        UNION

        SELECT
              mqt.pool_address
            , 'move' AS type
            , mqt.block_timestamp
            , mqt.block_number
            , CAST(NULL AS numeric) AS bucket_index
            , mqt.bucket_index_from
            , mqt.bucket_index_to
            , mqt.amount
        FROM {move_quote_token_table} mqt
        WHERE mqt.lender = %s

        ORDER BY block_number
    """.format(
        add_quote_token_table=chain.add_quote_token._meta.db_table,
        remove_quote_token_table=chain.remove_quote_token._meta.db_table,
        move_quote_token_table=chain.move_quote_token._meta.db_table,
    )
    with connection.cursor() as cursor:
        cursor.execute(sql, [wallet_address, wallet_address, wallet_address])
        events = fetch_all(cursor)

    for event in events:
        match event["type"]:
            case "add":
                curr_positions[event["pool_address"]]["supply"] += event["amount"]
            case "remove":
                curr_positions[event["pool_address"]]["supply"] -= event["amount"]
            case "move":
                # Doesn't affect total supply
                pass

        _update_current_positions_block(curr_positions, event)


def _handle_collateral_events(chain, wallet_address, from_block_number, curr_positions):
    # TODO: from_block_number
    sql = """
        SELECT
              x.pool_address
            , x.block_timestamp
            , x.block_number
            , SUM(x.amount) AS amount
        FROM (
            SELECT
                 ac.pool_address
               , ac.block_timestamp
               , ac.block_number
               , ac.amount
            FROM {add_collateral_table} AS ac
            WHERE ac.actor = %s

            UNION

            SELECT
                  rc.pool_address
                , rc.block_timestamp
                , rc.block_number
                , rc.amount * -1 AS amount
            FROM {remove_collateral_table} rc
            WHERE rc.claimer = %s
        ) x
        GROUP BY 1, 2, 3
        ORDER BY block_number
    """.format(
        add_collateral_table=chain.add_collateral._meta.db_table,
        remove_collateral_table=chain.remove_collateral._meta.db_table,
    )
    with connection.cursor() as cursor:
        cursor.execute(sql, [wallet_address, wallet_address])
        events = fetch_all(cursor)

    for event in events:
        curr_positions[event["pool_address"]]["collateral"] += event["amount"]
        _update_current_positions_block(curr_positions, event)


def save_wallet_positions(chain, wallet_address, from_block_number):
    curr_positions = defaultdict(lambda: defaultdict(Decimal))

    _handle_debt_events(chain, wallet_address, from_block_number, curr_positions)
    _handle_quote_token_events(chain, wallet_address, from_block_number, curr_positions)
    _handle_collateral_events(chain, wallet_address, from_block_number, curr_positions)

    # TODO: wallet_market_state

    for pool_address, pool_position in curr_positions.items():
        # Can't use update_or_create because we need to set some values to 0 only when
        # creating the model
        try:
            current_position = chain.current_position.objects.get(
                wallet_address=wallet_address, pool_address=pool_address
            )
        except chain.current_position.DoesNotExist:
            current_position = chain.current_position(
                wallet_address=wallet_address,
                pool_address=pool_address,
                debt=0,  # TODO: this should be updated here!
            )

        current_position.debt = pool_position["debt"]
        current_position.t0debt = pool_position["t0debt"]
        current_position.collateral = pool_position["collateral"]
        current_position.supply = pool_position["supply"]
        current_position.block_number = pool_position["block_number"]
        current_position.datetime = pool_position["datetime"]
        current_position.save()

    print(current_position.__dict__)
