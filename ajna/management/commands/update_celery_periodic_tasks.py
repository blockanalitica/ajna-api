import importlib

from django.conf import settings
from django.core.management.base import BaseCommand
from django_celery_beat.models import CrontabSchedule, PeriodicTask


class Command(BaseCommand):
    def handle(self, *args, **options):
        schedule_keys = []
        for celery_module in settings.CELERY_IMPORTS:
            module = importlib.import_module(celery_module)
            if hasattr(module, "SCHEDULE"):
                for key, value in module.SCHEDULE.items():
                    sch = value["schedule"]
                    schedule, _ = CrontabSchedule.objects.get_or_create(
                        minute=sch._orig_minute,
                        hour=sch._orig_hour,
                        day_of_week=sch._orig_day_of_week,
                        day_of_month=sch._orig_day_of_month,
                        month_of_year=sch._orig_month_of_year,
                    )
                    task = "{}.{}".format(celery_module, key)
                    PeriodicTask.objects.update_or_create(
                        name=task,
                        defaults={
                            "crontab": schedule,
                            "task": task,
                            "queue": value.get("queue")
                            or settings.CELERY_TASK_DEFAULT_QUEUE,
                        },
                    )
                    schedule_keys.append(task)

        old_tasks = PeriodicTask.objects.exclude(name__in=schedule_keys).exclude(
            name__istartswith="celery."
        )
        old_tasks.delete()

        self.stdout.write("Updated celery periodic tasks")
