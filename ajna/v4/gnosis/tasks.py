import logging
from datetime import date, datetime, timedelta

from celery.schedules import crontab

from ajna.celery_app import app

from ..modules.activity import sync_activity_snapshots
from ..modules.at_risk import wallets_at_risk_notification
from ..modules.events import fetch_and_save_events_for_all_pools
from ..modules.networks import save_network_stats_for_date
from ..modules.pools import (
    PoolERC20Manager,
    PoolERC721Manager,
    save_all_pools_volume_for_date,
)
from ..modules.positions import EventProcessor
from ..modules.prices import update_token_prices
from .chain import Gnosis, GnosisModels

log = logging.getLogger(__name__)

SCHEDULE = {
    "fetch_market_price_task": {
        "schedule": crontab(minute="*/1"),
    },
    "sync_activity_snapshots_task": {
        "schedule": crontab(minute="*/5"),
    },
    "fetch_erc20_pool_created_events_task": {
        "schedule": crontab(minute="0-59/5"),
    },
    "fetch_erc721_pool_created_events_task": {
        "schedule": crontab(minute="0-59/5"),
    },
    "fetch_erc20_pools_data_task": {
        "schedule": crontab(minute="1-59/5"),
    },
    "fetch_erc721_pools_data_task": {
        "schedule": crontab(minute="1-59/5"),
    },
    "fetch_and_save_events_for_all_pools_task": {
        "schedule": crontab(minute="1-59/5"),
    },
    "process_events_for_all_pools_task": {
        "schedule": crontab(minute="2-59/5"),
    },
    "save_wallets_at_risk_notification_task": {
        "schedule": crontab(minute="3-59/5"),
    },
    "save_all_pools_volume_for_today_task": {
        "schedule": crontab(minute="3-59/5"),
    },
    "save_network_stats_for_today_task": {
        "schedule": crontab(minute="3-59/5"),
    },
    "save_all_pools_volume_for_yesterday_task": {
        # Run 10 past midnight to make sure we get all events saved before taking
        # the snapshot
        "schedule": crontab(minute="10", hour="0"),
    },
    "save_network_stats_for_yesterday_task": {
        # Run 11 past midnight to make sure we get all events saved before taking
        # the snapshot
        "schedule": crontab(minute="11", hour="0"),
    },
}


@app.task
def fetch_market_price_task():
    models = GnosisModels()
    update_token_prices(models, network="gnosis")


@app.task
def fetch_erc20_pool_created_events_task():
    chain = Gnosis()
    erc20_manager = PoolERC20Manager(chain)
    erc20_manager.fetch_and_save_pool_created_events()


@app.task
def fetch_erc721_pool_created_events_task():
    chain = Gnosis()
    erc721_manager = PoolERC721Manager(chain)
    erc721_manager.fetch_and_save_pool_created_events()


@app.task
def fetch_erc20_pools_data_task():
    chain = Gnosis()
    erc20_manager = PoolERC20Manager(chain)
    erc20_manager.fetch_and_save_pools_data()


@app.task
def fetch_erc721_pools_data_task():
    chain = Gnosis()
    erc721_manager = PoolERC721Manager(chain)
    erc721_manager.fetch_and_save_pools_data()


@app.task
def fetch_and_save_events_for_all_pools_task():
    chain = Gnosis()
    fetch_and_save_events_for_all_pools(chain)


@app.task
def process_events_for_all_pools_task():
    chain = Gnosis()
    processor = EventProcessor(chain)
    processor.process_all_events()


@app.task
def save_all_pools_volume_for_yesterday_task():
    # This task should be ran a few minutes past midnight to make sure all events
    # are fetched and saved for the day before
    chain = Gnosis()
    yesterday = (datetime.now() - timedelta(days=1)).date()
    save_all_pools_volume_for_date(chain, yesterday)


@app.task
def save_all_pools_volume_for_today_task():
    chain = Gnosis()
    dt = datetime.now().date()
    save_all_pools_volume_for_date(chain, dt)


@app.task
def save_wallets_at_risk_notification_task():
    chain = Gnosis()
    wallets_at_risk_notification(chain)


@app.task
def save_network_stats_for_today_task():
    models = GnosisModels()
    dt = date.today()
    save_network_stats_for_date(models, dt, "gnosis")


@app.task
def save_network_stats_for_yesterday_task():
    # This task should be ran a few minutes past midnight to make sure all events
    # are fetched and saved for the day before
    models = GnosisModels()
    yesterday = (datetime.now() - timedelta(days=1)).date()
    save_network_stats_for_date(models, yesterday, "gnosis")


@app.task
def sync_activity_snapshots_task():
    chain = Gnosis()
    sync_activity_snapshots(chain)
