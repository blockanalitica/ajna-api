import logging
import threading
import time

import celery.signals
from celery import Celery
from celery.signals import setup_logging

from ajna.metrics import gauge, raw_timer, statsd_client

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
        return "{}.{}".format(prefix, task)
    else:
        return "{}.{}".format(prefix, task.name)


def _start_timer(name, group, instance):
    try:
        _state.timers[(name, group, instance)] = time.time()
    except AttributeError:
        _state.timers = {(name, group, instance): time.time()}


def _stop_timer(name, group, instance):
    try:
        start = _state.timers.pop((name, group, instance))
    except (AttributeError, KeyError):
        return

    total = time.time() - start

    raw_timer(f"{group}.{name}", total * 1000)


def _inc_counter(name, group):
    statsd_client.incr(f"{group}.{name}")


def _send_queue_sizes_to_statsd():
    global _prev_queue_size_check
    # Limit sending queue sizes to statsd to every 5 seconds as to not spam stats
    # on every task execution which might kill statsd :)

    try:
        if (time.time() - _prev_queue_size_check) < 5:
            return

        _prev_queue_size_check = time.time()
        queues = ["default", "compute", "priority"]
        with app.pool.acquire(block=True) as conn:
            for queue in queues:
                queue_size = conn.default_channel.client.llen(queue)
                gauge("celery.queues.{}.size".format(queue), queue_size)
    except Exception:
        log.exception("Error sending queue sizes to statsd")


@celery.signals.before_task_publish.connect
def statsd_before_task_publish(sender, body, headers, **kwargs):
    task_id = headers.get("id") or body.get("id")
    _start_timer("enqueue", _celery_task_key(sender), task_id)


@celery.signals.after_task_publish.connect
def statsd_after_task_publish(sender, body, headers, **kwargs):
    task_id = headers.get("id") or body.get("id")
    _stop_timer("enqueue", _celery_task_key(sender), task_id)


@celery.signals.task_prerun.connect
def statsd_task_prerun(sender, task_id, **kwargs):
    _start_timer("run", _celery_task_key(sender), task_id)


@celery.signals.task_postrun.connect
def statsd_task_postrun(sender, task_id, **kwargs):
    _stop_timer("run", _celery_task_key(sender), task_id)
    # On postrun, send queue sizes to statsd
    _send_queue_sizes_to_statsd()


@celery.signals.task_retry.connect
def statsd_task_retry(sender, **kwargs):
    _inc_counter("retry", _celery_task_key(sender))


@celery.signals.task_success.connect
def statsd_task_success(sender, **kwargs):
    _inc_counter("success", _celery_task_key(sender))


@celery.signals.task_failure.connect
def statsd_task_failure(sender, **kwargs):
    _inc_counter("failure", _celery_task_key(sender))


@celery.signals.task_revoked.connect
def statsd_task_revoked(sender, **kwargs):
    _inc_counter("revoked", _celery_task_key(sender))
