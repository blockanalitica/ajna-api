import logging

from ajna.celery import app

from ..modules.events import fetch_and_save_events_for_all_pools
from ..modules.pools import fetch_and_save_pools_data, fetch_new_pools
from ..modules.positions import EventProcessor
from ..modules.prices import update_token_prices
from .chain import Goerli, GoerliModels

# from ..modules.positions import EventProcessor

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
}


@app.task
def fetch_market_price_task():
    models = GoerliModels()
    update_token_prices(models, network="goerli")


@app.task
def fetch_new_pools_task():
    chain = Goerli()
    fetch_new_pools(chain)


@app.task
def fetch_and_save_pools_data_task():
    chain = Goerli()
    fetch_and_save_pools_data(chain)


@app.task
def fetch_and_save_events_for_all_pools_task():
    chain = Goerli()
    fetch_and_save_events_for_all_pools(chain)


@app.task
def process_events_for_all_pools_task():
    chain = Goerli()
    pool_addresses = list(chain.pool.objects.all().values_list("address", flat=True))

    for pool_address in pool_addresses:
        processor = EventProcessor(chain, pool_address)
        processor.process_events()
