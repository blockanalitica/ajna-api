import logging
import threading
import time

import celery.signals
from celery import Celery
from celery.signals import setup_logging

from ajna.metrics import gauge, increment, raw_timer, shutdown

log = logging.getLogger(__name__)

_state = threading.local()

_prev_queue_size_check = 0

app = Celery("ajna")
app.config_from_object("django.conf:settings", namespace="CELERY")


@setup_logging.connect
def config_loggers(*args, **kwargs):
    from logging.config import dictConfig

    from django.conf import settings

    dictConfig(settings.LOGGING)


def _celery_task_key(task):
    prefix = "celery"
    if isinstance(task, str):
        return f"{prefix}.{task}"
    else:
        return f"{prefix}.{task.name}"


def _start_timer(name, group, instance):
    if not hasattr(_state, "timers"):
        _state.timers = {}
    _state.timers[(name, group, instance)] = time.perf_counter()


def _stop_timer(name, group, instance):
    try:
        start = _state.timers.pop((name, group, instance))
    except (AttributeError, KeyError):
        return

    total = time.perf_counter() - start

    raw_timer(f"{group}.{name}", total * 1000)


def _inc_counter(name, group):
    increment(f"{group}.{name}", prefix="")


def _send_queue_sizes_to_metrics():
    global _prev_queue_size_check

    try:
        if (time.perf_counter() - _prev_queue_size_check) < 5:
            return

        _prev_queue_size_check = time.perf_counter()
        queues = ["default", "compute", "priority"]
        with app.pool.acquire(block=True) as conn:
            for queue in queues:
                queue_size = conn.default_channel.client.llen(queue)
                gauge(f"celery.queues.{queue}.size", queue_size)
    except Exception:
        log.exception("Error sending queue sizes to metrics")


@celery.signals.before_task_publish.connect
def metrics_before_task_publish(sender, body, headers, **kwargs):
    task_id = headers.get("id") or body.get("id")
    _start_timer("enqueue", _celery_task_key(sender), task_id)


@celery.signals.after_task_publish.connect
def metrics_after_task_publish(sender, body, headers, **kwargs):
    task_id = headers.get("id") or body.get("id")
    _stop_timer("enqueue", _celery_task_key(sender), task_id)


@celery.signals.task_prerun.connect
def metrics_task_prerun(sender, task_id, **kwargs):
    _start_timer("run", _celery_task_key(sender), task_id)


@celery.signals.task_postrun.connect
def metrics_task_postrun(sender, task_id, **kwargs):
    _stop_timer("run", _celery_task_key(sender), task_id)
    _send_queue_sizes_to_metrics()


@celery.signals.task_retry.connect
def metrics_task_retry(sender, **kwargs):
    _inc_counter("retry", _celery_task_key(sender))


@celery.signals.task_success.connect
def metrics_task_success(sender, **kwargs):
    _inc_counter("success", _celery_task_key(sender))


@celery.signals.task_failure.connect
def metrics_task_failure(sender, **kwargs):
    _inc_counter("failure", _celery_task_key(sender))


@celery.signals.task_revoked.connect
def metrics_task_revoked(sender, **kwargs):
    _inc_counter("revoked", _celery_task_key(sender))


@celery.signals.worker_process_shutdown.connect
@celery.signals.worker_shutdown.connect
def shutdown_metrics(**kwargs):
    shutdown()
