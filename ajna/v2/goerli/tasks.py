import logging

from ajna.celery import app

from ..modules.prices import update_token_prices
from .chain import GoerliModels

# from ..modules.positions import EventProcessor

log = logging.getLogger(__name__)

SCHEDULE = {
    # "fetch_market_price_task": {
    #     "schedule": crontab(minute="*/1"),
    # },
}


@app.task
def fetch_market_price_task():
    models = GoerliModels()
    update_token_prices(models, network="goerli")


# @app.task
# def start_processing_all_pool_events():
#     models = GoerliModels()
#     pool_addresses = models.pool.objects.all().values_list("address", flat=True)
#     for pool_address in pool_addresses:
#         process_event_for_pool_task.delay(pool_address)


# @app.task
# def process_event_for_pool_task(pool_address):
#     chain = Goerli()
#     processor = EventProcessor(chain, pool_address)
#     processor.process_events()
