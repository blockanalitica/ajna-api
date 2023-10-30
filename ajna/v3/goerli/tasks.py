import logging
from datetime import datetime, timedelta

from celery.schedules import crontab

from ajna.celery import app

from ..modules.events import fetch_and_save_events_for_all_pools
from ..modules.grants import fetch_and_save_grant_proposals
from ..modules.pools import (
    PoolERC20Manager,
    PoolERC721Manager,
    save_all_pools_volume_for_date,
)
from ..modules.positions import EventProcessor
from ..modules.prices import update_token_prices
from .chain import Goerli, GoerliModels

log = logging.getLogger(__name__)

SCHEDULE = {
    "fetch_market_price_task": {
        "schedule": crontab(minute="*/1"),
    },
    # "fetch_and_save_events_for_all_pools_task": {
    #     "schedule": crontab(minute="*/2"),
    # },
    "fetch_erc20_pool_created_events_task": {
        "schedule": crontab(minute="*/5"),
    },
    "fetch_erc721_pool_created_events_task": {
        "schedule": crontab(minute="*/5"),
    },
    # "fetch_erc20_pools_data_task": {
    #     "schedule": crontab(minute="*/5"),
    # },
    # "fetch_erc721_pools_data_task": {
    #     "schedule": crontab(minute="*/5"),
    # },
    # "process_events_for_all_pools_task": {
    #     "schedule": crontab(minute="*/5"),
    # },
    # "fetch_and_save_grant_proposals_task": {
    #     "schedule": crontab(minute="*/5"),
    # },
    # "save_all_pools_volume_for_yesterday_task": {
    #     # Run 10 past midnight to make sure we get all events saved before taking
    #     # the snapshot
    #     "schedule": crontab(minute="10", hour="0"),
    # },
}


@app.task
def fetch_market_price_task():
    models = GoerliModels()
    update_token_prices(models, network="goerli")


@app.task
def fetch_erc20_pool_created_events_task():
    chain = Goerli()
    erc20_manager = PoolERC20Manager(chain)
    erc20_manager.fetch_and_save_pool_created_events()


@app.task
def fetch_erc721_pool_created_events_task():
    chain = Goerli()
    erc20_manager = PoolERC721Manager(chain)
    erc20_manager.fetch_and_save_pool_created_events()


@app.task
def fetch_erc20_pools_data_task():
    chain = Goerli()
    erc20_manager = PoolERC20Manager(chain)
    erc20_manager.fetch_and_save_pools_data()


@app.task
def fetch_erc721_pools_data_task():
    chain = Goerli()
    erc20_manager = PoolERC721Manager(chain)
    erc20_manager.fetch_and_save_pools_data()


@app.task
def fetch_and_save_events_for_all_pools_task():
    chain = Goerli()
    fetch_and_save_events_for_all_pools(chain)


@app.task
def process_events_for_all_pools_task():
    chain = Goerli()
    processor = EventProcessor(chain)
    processor.process_all_events()


@app.task
def save_all_pools_volume_for_yesterday_task():
    # This task should be ran a few minutes past midnight to make sure all events
    # are fetched and saved for the day before
    chain = Goerli()
    yesterday = (datetime.now() - timedelta(days=1)).date()
    save_all_pools_volume_for_date(chain, yesterday)


@app.task
def fetch_and_save_grant_proposals_task():
    chain = Goerli()
    fetch_and_save_grant_proposals(chain)
