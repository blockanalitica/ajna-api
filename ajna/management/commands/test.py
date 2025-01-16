import importlib

# from django.conf import settings
from django.core.management.base import BaseCommand

# from django_celery_beat.models import CrontabSchedule, PeriodicTask
from ajna.v4.avalanche.tasks import (
    fetch_erc20_pool_created_events_task,
    fetch_erc721_pool_created_events_task,
    fetch_erc20_pools_data_task,
    fetch_erc721_pools_data_task,
    fetch_and_save_events_for_all_pools_task,
    process_events_for_all_pools_task,
    save_all_pools_volume_for_yesterday_task,
    save_all_pools_volume_for_today_task,
    save_wallets_at_risk_notification_task,
    save_network_stats_for_today_task,
    save_network_stats_for_yesterday_task,
    sync_activity_snapshots_task,
    fetch_market_price_task
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        fetch_erc20_pool_created_events_task()
        fetch_erc721_pool_created_events_task()
        fetch_erc20_pools_data_task()
        fetch_erc721_pools_data_task()
        fetch_and_save_events_for_all_pools_task()
        process_events_for_all_pools_task()
        save_all_pools_volume_for_yesterday_task()
        save_all_pools_volume_for_today_task()
        save_wallets_at_risk_notification_task()
        save_network_stats_for_today_task()
        save_network_stats_for_yesterday_task()
        sync_activity_snapshots_task()
        fetch_market_price_task()
