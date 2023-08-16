from collections import defaultdict
from datetime import datetime
from decimal import Decimal

from django.db import connection

from ajna.utils.db import fetch_all

POOL_INFLATORS = defaultdict(dict)


def _get_inflator(chain, pool_address, block_number):
    global POOL_INFLATORS

    if block_number not in POOL_INFLATORS[pool_address]:
        calls = [
            (
                chain.pool_info_address,
                [
                    "poolLoansInfo(address)((uint256,uint256,address,uint256,uint256))",
                    pool_address,
                ],
                [pool_address, None],
            )
        ]

        data = chain.call_multicall(calls, block_id=block_number)
        POOL_INFLATORS[pool_address][block_number] = data[pool_address][3] / Decimal(
            "1e18"
        )

    return POOL_INFLATORS[pool_address][block_number]


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
              x.pool_address
            , x.block_timestamp
            , x.block_number
            , SUM(x.debt) AS debt
            , SUM(x.collateral) AS collateral
        FROM (
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
        ) x
        GROUP BY 1, 2, 3
        ORDER BY block_number
    """.format(
        draw_debt_table=chain.draw_debt._meta.db_table,
        repay_debt_table=chain.repay_debt._meta.db_table,
    )
    with connection.cursor() as cursor:
        cursor.execute(sql, [wallet_address, wallet_address])
        events = fetch_all(cursor)

    for event in events:
        inflator = _get_inflator(chain, event["pool_address"], event["block_number"])
        curr_positions[event["pool_address"]]["debt"] += event["debt"]
        # Round to 18 decimals as our model accepts only 18 decimals
        curr_positions[event["pool_address"]]["t0debt"] += round(
            event["debt"] / inflator, 18
        )
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
