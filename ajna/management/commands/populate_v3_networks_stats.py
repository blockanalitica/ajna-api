from datetime import date, timedelta

from django.core.management.base import BaseCommand

from ajna.v3.arbitrum.chain import ArbitrumModels
from ajna.v3.base.chain import BaseModels
from ajna.v3.ethereum.chain import EthereumModels
from ajna.v3.modules.networks import save_network_stats_for_date
from ajna.v3.optimism.chain import OptimismModels
from ajna.v3.polygon.chain import PolygonModels


class Command(BaseCommand):
    def handle(self, *args, **options):
        chain_models_map = {
            "ethereum": EthereumModels(),
            "arbitrum": ArbitrumModels(),
            "base": BaseModels(),
            "optimism": OptimismModels(),
            "polygon": PolygonModels(),
        }

        start_date = date(2024, 1, 8)

        num_days = (date.today() - start_date).days + 1
        for x in range(num_days):
            dt = start_date + timedelta(days=x)

            for key, models in chain_models_map.items():
                save_network_stats_for_date(models, dt, key)
