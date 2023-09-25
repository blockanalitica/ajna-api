import logging
from datetime import datetime, timedelta

from ajna.celery import app

from ..modules.events import fetch_and_save_events_for_all_pools
from ..modules.pools import (
    fetch_and_save_pools_data,
    fetch_new_pools,
    save_all_pools_volume_for_date,
)
from ..modules.positions import EventProcessor
from ..modules.prices import update_token_prices
from .chain import Ethereum, EthereumModels

log = logging.getLogger(__name__)

SCHEDULE = {
    # "fetch_market_price_task": {
    #     "schedule": crontab(minute="*/1"),
    # },
    # "fetch_and_save_events_for_all_pools_task": {
    #     "schedule": crontab(minute="*/2"),
    # },
    # "fetch_new_pools_task": {
    #     "schedule": crontab(minute="*/5"),
    # },
    # "fetch_and_save_pools_data_task": {
    #         "schedule": crontab(minute="*/5"),
    #     },
    # "process_events_for_all_pools_task": {
    #         "schedule": crontab(minute="*/5"),
    #     },
    # "save_all_pools_volume_for_yesterday_task": {
    #     # Run 10 past midnight to make sure we get all events saved before taking
    #     # the snapshot
    #     "schedule": crontab(minute="10", hour="0"),
    # },
}


@app.task
def fetch_market_price_task():
    models = EthereumModels()
    update_token_prices(models)


@app.task
def fetch_new_pools_task():
    chain = Ethereum()
    fetch_new_pools(chain)


@app.task
def fetch_and_save_pools_data_task():
    chain = Ethereum()
    fetch_and_save_pools_data(chain)


@app.task
def fetch_and_save_events_for_all_pools_task():
    chain = Ethereum()
    fetch_and_save_events_for_all_pools(chain)


@app.task
def process_events_for_all_pools_task():
    chain = Ethereum()
    pool_addresses = list(chain.pool.objects.all().values_list("address", flat=True))

    for pool_address in pool_addresses:
        processor = EventProcessor(chain, pool_address)
        processor.process_events()


@app.task
def save_all_pools_volume_for_yesterday_task():
    # This task should be ran a few minutes past midnight to make sure all events
    # are fetched and saved for the day before
    chain = Ethereum()
    yesterday = (datetime.now() - timedelta(days=1)).date()
    save_all_pools_volume_for_date(chain, yesterday)
