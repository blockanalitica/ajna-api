import logging

from ajna.celery import app

from ..modules.prices import update_token_prices
from .chain import EthereumModels

log = logging.getLogger(__name__)

SCHEDULE = {
    # "fetch_market_price_task": {
    #     "schedule": crontab(minute="*/1"),
    # },
}


@app.task
def fetch_market_price_task():
    models = EthereumModels()
    update_token_prices(models)
