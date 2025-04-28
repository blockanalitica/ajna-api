import logging
from datetime import date, datetime, timedelta

from celery.schedules import crontab

from ajna.celery_app import app
from ajna.v4.modules.at_risk import wallets_at_risk_notification
from ajna.v4.modules.events import fetch_and_save_events_for_all_pools
from ajna.v4.modules.networks import save_network_stats_for_date
from ajna.v4.modules.pools import (
    PoolERC20Manager,
    PoolERC721Manager,
    save_all_pools_volume_for_date,
)
from ajna.v4.modules.positions import EventProcessor
from ajna.v4.modules.prices import update_token_prices

from .chain import Polygon, PolygonModels

log = logging.getLogger(__name__)

SCHEDULE = {
    "fetch_market_price_task": {
        "schedule": crontab(minute="*/1"),
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
    models = PolygonModels()
    update_token_prices(models, network="polygon")


@app.task
def fetch_erc20_pool_created_events_task():
    chain = Polygon()
    erc20_manager = PoolERC20Manager(chain)
    erc20_manager.fetch_and_save_pool_created_events()


@app.task
def fetch_erc721_pool_created_events_task():
    chain = Polygon()
    erc721_manager = PoolERC721Manager(chain)
    erc721_manager.fetch_and_save_pool_created_events()


@app.task
def fetch_erc20_pools_data_task():
    chain = Polygon()
    erc20_manager = PoolERC20Manager(chain)
    erc20_manager.fetch_and_save_pools_data()


@app.task
def fetch_erc721_pools_data_task():
    chain = Polygon()
    erc721_manager = PoolERC721Manager(chain)
    erc721_manager.fetch_and_save_pools_data()


@app.task
def fetch_and_save_events_for_all_pools_task():
    chain = Polygon()
    fetch_and_save_events_for_all_pools(chain)


@app.task
def process_events_for_all_pools_task():
    chain = Polygon()
    processor = EventProcessor(chain)
    processor.process_all_events()


@app.task
def save_all_pools_volume_for_yesterday_task():
    # This task should be ran a few minutes past midnight to make sure all events
    # are fetched and saved for the day before
    chain = Polygon()
    yesterday = (datetime.now() - timedelta(days=1)).date()
    save_all_pools_volume_for_date(chain, yesterday)


@app.task
def save_all_pools_volume_for_today_task():
    chain = Polygon()
    dt = datetime.now().date()
    save_all_pools_volume_for_date(chain, dt)


@app.task
def save_wallets_at_risk_notification_task():
    chain = Polygon()
    wallets_at_risk_notification(chain)


@app.task
def save_network_stats_for_today_task():
    models = PolygonModels()
    dt = date.today()
    save_network_stats_for_date(models, dt, "polygon")


@app.task
def save_network_stats_for_yesterday_task():
    # This task should be ran a few minutes past midnight to make sure all events
    # are fetched and saved for the day before
    models = PolygonModels()
    yesterday = (datetime.now() - timedelta(days=1)).date()
    save_network_stats_for_date(models, yesterday, "polygon")
