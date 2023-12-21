import logging
from datetime import datetime, timedelta

from ajna.celery import app

from ..modules.at_risk import wallets_at_risk_notification
from ..modules.events import fetch_and_save_events_for_all_pools
from ..modules.grants import fetch_and_save_grant_proposals
from ..modules.pools import (
    PoolERC20Manager,
    PoolERC721Manager,
    save_all_pools_volume_for_date,
)
from ..modules.positions import EventProcessor
from ..modules.prices import update_token_prices
from .chain import Ethereum, EthereumModels

# from celery.schedules import crontab


log = logging.getLogger(__name__)

SCHEDULE = {
    # "fetch_market_price_task": {
    #     "schedule": crontab(minute="*/1"),
    # },
    # "fetch_and_save_events_for_all_pools_task": {
    #     "schedule": crontab(minute="*/2"),
    # },
    # "fetch_erc20_pool_created_events_task": {
    #     "schedule": crontab(minute="*/5"),
    # },
    # "fetch_erc721_pool_created_events_task": {
    #     "schedule": crontab(minute="*/5"),
    # },
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
    # "save_wallets_at_risk_notification_task": {
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
    models = EthereumModels()
    update_token_prices(models, network="ethereum")


@app.task
def fetch_erc20_pool_created_events_task():
    chain = Ethereum()
    erc20_manager = PoolERC20Manager(chain)
    erc20_manager.fetch_and_save_pool_created_events()


@app.task
def fetch_erc721_pool_created_events_task():
    chain = Ethereum()
    erc721_manager = PoolERC721Manager(chain)
    erc721_manager.fetch_and_save_pool_created_events()


@app.task
def fetch_erc20_pools_data_task():
    chain = Ethereum()
    erc20_manager = PoolERC20Manager(chain)
    erc20_manager.fetch_and_save_pools_data()


@app.task
def fetch_erc721_pools_data_task():
    chain = Ethereum()
    erc721_manager = PoolERC721Manager(chain)
    erc721_manager.fetch_and_save_pools_data()


@app.task
def fetch_and_save_events_for_all_pools_task():
    chain = Ethereum()
    fetch_and_save_events_for_all_pools(chain)


@app.task
def process_events_for_all_pools_task():
    chain = Ethereum()
    processor = EventProcessor(chain)
    processor.process_all_events()


@app.task
def save_all_pools_volume_for_yesterday_task():
    # This task should be ran a few minutes past midnight to make sure all events
    # are fetched and saved for the day before
    chain = Ethereum()
    yesterday = (datetime.now() - timedelta(days=1)).date()
    save_all_pools_volume_for_date(chain, yesterday)


@app.task
def fetch_and_save_grant_proposals_task():
    chain = Ethereum()
    fetch_and_save_grant_proposals(chain)


@app.task
def save_wallets_at_risk_notification_task():
    chain = Ethereum()
    wallets_at_risk_notification(chain)
