from functools import wraps

import statsd
from django.conf import settings

statsd_client = statsd.StatsClient(
    settings.STATSD_HOST, settings.STATSD_PORT, settings.STATSD_PREFIX
)


class Timer:
    """Metrics wrapper for Statsd Timer Object

    >>> import time
    >>> with metrics.Timer('unique_key'):
    ...     time.sleep(1)
    """

    def __init__(self, key):
        self.timer = statsd_client.timer(str(key))
        self.key = key

    def __enter__(self):
        self.timer.start()

    def __exit__(self, type_, value, traceback):
        self.timer.stop()


def timerd(key):
    """
    Decorator function to set up a timer around a function call.
    This is a function only decorator!

    Example:
    >>> import time
    >>> @metrics.timerd('time_sleep_key')
    >>> def timed_function():
    ...     time.sleep(1)
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not key:
                raise Exception("Using an empty key name")
            with Timer(key):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def raw_timer(key, value):
    """Send a timing directly to Graphite, without need to call start() and stop().

    :keyword value: The time in seconds, it must be an int or a float

    >>> # Got a timing from frontend!
    >>> metrics.raw_timer('unique_key', 31.3)
    """

    # Validating "value" to be an int or a float
    if not isinstance(value, (int, float)):
        return None

    return statsd_client.timing(str(key), value)


def increment(key, delta=1, subname=None):
    """Increment the counter identified with `key` and `subname` with `delta`

    >>> # After a user logs in....
    >>> metrics.increment('auth.successful_login', 1)

        :keyword delta: The delta to add to the counter, default is 1
        :keyword subname: The subname to report the data to (appended to the
            client name). Like "hits", or "sales".
    """
    name = f"counters.{key}"
    if subname:
        name += f".{subname}"

    return statsd_client.incr(name, delta)


def decrement(key, delta=1, subname=None):
    """Decrement the counter identified with `key` and `subname` with `delta`

    >>> # Users that log out...
    >>> metrics.decrement('auth.connected_users', 1)

        :keyword delta: The delta to substract from the counter, default is 1
        :keyword subname: The subname to report the data to (appended to the
            client name)
    """

    name = f"counters.{key}"
    if subname:
        name += f".{subname}"

    return statsd_client.decr(name, delta)


def gauge(key, value=1, subname=None):
    """Set the value of the gauge identified with `key` and `subname` with `value`

    :keyword value: The value to set the gauge at, default is 1
    :keyword subname: The subname to report the data to (appended to the
        client name)
    """

    name = key
    if subname:
        name += f".{subname}"

    # We never use the relative changes behaviour so attempt to always make it do the
    # set value behaviour instead.
    if value < 0:
        statsd_client.gauge(name, 0)
    return statsd_client.gauge(name, value)


def function_long_name(func, extra=None):
    if extra:
        return ".".join([func.__module__, func.__name__, extra])
    else:
        return ".".join([func.__module__, func.__name__])


def auto_named_statsd_timer(function_to_decorate):
    call_name = function_long_name(function_to_decorate, "call")

    @wraps(function_to_decorate)
    def incr_and_call(*args, **kwargs):
        statsd_client.incr(call_name)
        return function_to_decorate(*args, **kwargs)

    timer_name = function_long_name(function_to_decorate, "time")
    named_decorator = statsd_client.timer(timer_name)

    return named_decorator(incr_and_call)
