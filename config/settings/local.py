from config.settings.base import *  # noqa
from config.settings.base import INSTALLED_APPS, MIDDLEWARE

DEBUG = True

CORS_ALLOW_ALL_ORIGINS = True

INSTALLED_APPS += [
    "debug_toolbar",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
] + MIDDLEWARE

SHELL_PLUS_PRINT_SQL = False

CELERY_TASK_ALWAYS_EAGER = True

SHELL_PLUS_IMPORTS = [
    "from ajna.v1.modules.pools import *",
    "from ajna.v1.goerli.tasks import *",
]

CACHE_MIDDLEWARE_SECONDS = 0


def _show_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": _show_toolbar,
}
