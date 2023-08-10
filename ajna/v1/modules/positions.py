from datetime import datetime
from decimal import Decimal
from collections import defaultdict
from django.db import connection

from ajna.utils.db import fetch_all


def _update_current_positions_block(current_position, event):
    # Only update block_number and datetime if event's block_number is greater
    # than the existing one as otherwise we might store the wrong block_number
    # since we're processing different events separately
    if event["block_number"] > current_position[event["pool_address"]]["block_number"]:
        current_position[event["pool_address"]]["block_number"] = event["block_number"]
        current_position[event["pool_address"]]["datetime"] = datetime.fromtimestamp(
            event["block_timestamp"]
        )


def _handle_debt_events(models, wallet_address, from_block_number, curr_positions):
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
        draw_debt_table=models.draw_debt._meta.db_table,
        repay_debt_table=models.repay_debt._meta.db_table,
    )
    with connection.cursor() as cursor:
        cursor.execute(sql, [wallet_address, wallet_address])
        events = fetch_all(cursor)

    for event in events:
        curr_positions[event["pool_address"]]["t0debt"] += event["debt"]
        curr_positions[event["pool_address"]]["collateral"] += event["collateral"]
        _update_current_positions_block(curr_positions, event)


def _handle_quote_token_events(
    models, wallet_address, from_block_number, curr_positions
):
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
        add_quote_token_table=models.add_quote_token._meta.db_table,
        remove_quote_token_table=models.remove_quote_token._meta.db_table,
        move_quote_token_table=models.move_quote_token._meta.db_table,
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


def save_wallet_positions(models, wallet_address, from_block_number):
    curr_positions = defaultdict(lambda: defaultdict(Decimal))

    _handle_debt_events(models, wallet_address, from_block_number, curr_positions)
    _handle_quote_token_events(
        models, wallet_address, from_block_number, curr_positions
    )

    # TODO: wallet_market_state

    for pool_address, pool_position in curr_positions.items():
        # Can't use update_or_create because we need to set some values to 0 only when
        # creating the model
        try:
            current_position = models.current_position.objects.get(
                wallet_address=wallet_address, pool_address=pool_address
            )
        except models.current_position.DoesNotExist:
            current_position = models.current_position(
                wallet_address=wallet_address,
                pool_address=pool_address,
                debt=0,  # TODO: this should be updated here!
            )

        current_position.t0debt = pool_position["t0debt"]
        current_position.collateral = pool_position["collateral"]
        current_position.supply = pool_position["supply"]
        current_position.block_number = pool_position["block_number"]
        current_position.datetime = pool_position["datetime"]
        current_position.save()
