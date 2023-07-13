import logging
from datetime import datetime, timedelta

from celery.schedules import crontab

from ajna.celery import app
from ajna.v1.modules.auctions import (
    fetch_and_save_active_liquidation_auctions,
    fetch_and_save_settled_liquidation_auctions,
)

from ...sources.subgraph import EthereumSubgraph
from ..modules.events import (
    fetch_and_save_add_collaterals,
    fetch_and_save_add_quote_tokens,
    fetch_and_save_draw_debts,
    fetch_and_save_remove_collaterals,
    fetch_and_save_remove_quote_tokens,
    fetch_and_save_repay_debts,
)
from ..modules.pools import (
    calculate_pool_volume_for_date,
    fetch_pools_data,
    update_token_prices,
)
from .chain import Ethereum, EthereumModels

log = logging.getLogger(__name__)

SCHEDULE = {
    "fetch_market_price_task": {
        "schedule": crontab(minute="*/1"),
    },
    "sync_liquidation_auctions_tasks": {
        "schedule": crontab(minute="*/5"),
    },
    "fetch_pools_data_task": {
        "schedule": crontab(minute="*/5"),
    },
    "save_remove_collateral_events_task": {
        "schedule": crontab(minute="*/5"),
    },
    "save_add_collateral_events_task": {
        "schedule": crontab(minute="*/5"),
    },
    "save_add_quote_token_events_tasks": {
        "schedule": crontab(minute="*/5"),
    },
    "save_remove_quote_token_events_tasks": {
        "schedule": crontab(minute="*/5"),
    },
    "save_draw_debts_events_tasks": {
        "schedule": crontab(minute="*/5"),
    },
    "save_repay_debts_events_tasks": {
        "schedule": crontab(minute="*/5"),
    },
    # "save_pools_data_snapshot_task": {
    #     "schedule": crontab(minute="1", hour="*/1"),
    # },
    "calculate_pool_volume_for_yesterday_task": {
        # Run 10 past midnight to make sure we get all events saved before taking
        # the snapshot
        "schedule": crontab(minute="10", hour="0"),
    },
}


@app.task
def fetch_market_price_task():
    models = EthereumModels()
    update_token_prices(models.token, models.price_feed)


@app.task
def fetch_pools_data_task():
    models = EthereumModels()
    chain = Ethereum()
    subgraph = EthereumSubgraph()
    fetch_pools_data(chain, subgraph, models)


# @app.task
# def save_pools_data_snapshot_task():
#     models = EthereumModels()
#     save_pools_data_snapshot(models)


@app.task
def save_remove_collateral_events_task():
    models = EthereumModels()
    block_number = (
        models.remove_collateral.objects.all()
        .order_by("-block_number")
        .values("block_number")[:1]
    )
    if block_number:
        last_block_number = block_number[0]["block_number"]
    else:
        last_block_number = 0

    subgraph = EthereumSubgraph()
    fetch_and_save_remove_collaterals(
        subgraph, models.remove_collateral, models.price_feed, last_block_number
    )


@app.task
def save_add_collateral_events_task():
    models = EthereumModels()
    block_number = (
        models.add_collateral.objects.all()
        .order_by("-block_number")
        .values("block_number")[:1]
    )
    if block_number:
        last_block_number = block_number[0]["block_number"]
    else:
        last_block_number = 0

    subgraph = EthereumSubgraph()
    fetch_and_save_add_collaterals(
        subgraph, models.add_collateral, models.price_feed, last_block_number
    )


@app.task
def save_add_quote_token_events_tasks():
    models = EthereumModels()
    block_number = (
        models.add_quote_token.objects.all()
        .order_by("-block_number")
        .values("block_number")[:1]
    )
    if block_number:
        last_block_number = block_number[0]["block_number"]
    else:
        last_block_number = 0

    subgraph = EthereumSubgraph()
    fetch_and_save_add_quote_tokens(
        subgraph, models.add_quote_token, models.price_feed, last_block_number
    )


@app.task
def save_remove_quote_token_events_tasks():
    models = EthereumModels()
    block_number = (
        models.remove_quote_token.objects.all()
        .order_by("-block_number")
        .values("block_number")[:1]
    )
    if block_number:
        last_block_number = block_number[0]["block_number"]
    else:
        last_block_number = 0

    subgraph = EthereumSubgraph()
    fetch_and_save_remove_quote_tokens(
        subgraph, models.remove_quote_token, models.price_feed, last_block_number
    )


@app.task
def save_draw_debts_events_tasks():
    models = EthereumModels()
    block_number = (
        models.draw_debt.objects.all()
        .order_by("-block_number")
        .values("block_number")[:1]
    )
    if block_number:
        last_block_number = block_number[0]["block_number"]
    else:
        last_block_number = 0
    subgraph = EthereumSubgraph()
    fetch_and_save_draw_debts(
        subgraph, models.draw_debt, models.price_feed, last_block_number
    )


@app.task
def save_repay_debts_events_tasks():
    models = EthereumModels()
    block_number = (
        models.repay_debt.objects.all()
        .order_by("-block_number")
        .values("block_number")[:1]
    )
    if block_number:
        last_block_number = block_number[0]["block_number"]
    else:
        last_block_number = 0

    subgraph = EthereumSubgraph()
    fetch_and_save_repay_debts(
        subgraph, models.repay_debt, models.price_feed, last_block_number
    )


@app.task
def sync_liquidation_auctions_tasks():
    models = EthereumModels()
    settle_time = (
        models.liqudation_auction.objects.filter(settled=True)
        .order_by("-settle_time")
        .values("settle_time")[:1]
    )
    if settle_time:
        last_settle_time = settle_time[0]["settle_time"]
    else:
        last_settle_time = 0

    subgraph = EthereumSubgraph()
    fetch_and_save_settled_liquidation_auctions(
        subgraph, models.liqudation_auction, models.price_feed, last_settle_time
    )
    subgraph = EthereumSubgraph()
    fetch_and_save_active_liquidation_auctions(subgraph, models.liqudation_auction)


@app.task
def calculate_pool_volume_for_yesterday_task():
    # This task should be ran a few minutes past midnight to make sure all events
    # are fetched and saved for the day before
    models = EthereumModels()
    yesterday = (datetime.now() - timedelta(days=1)).date()
    calculate_pool_volume_for_date(models, yesterday)
