import sys
from pathlib import Path

import environ
import sentry_sdk
from corsheaders.defaults import default_headers
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import ignore_logger

env = environ.Env()
environ.Env.read_env(env_file=".env")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env("AJNA_SECRET_KEY", default="django-insecure-bzupfio1t7h")

DEBUG = env.bool("AJNA_DEBUG", default=False)

ALLOWED_HOSTS = [
    host
    for host in env("AJNA_ALLOWED_HOSTS", default="localhost;0.0.0.0;127.0.0.1").split(
        ";"
    )
    if host
]

INTERNAL_IPS = [ip for ip in env("AJNA_INTERNAL_IPS", default="").split(";") if ip]

CORS_ALLOWED_ORIGINS = [
    cors for cors in env("AJNA_CORS_ALLOWED_ORIGINS", default="").split(";") if cors
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    cors
    for cors in env("AJNA_CORS_ALLOWED_ORIGIN_REGEXES", default="").split(";")
    if cors
]

CORS_ALLOW_HEADERS = list(default_headers) + [
    "sentry-trace",
]
CSRF_TRUSTED_ORIGINS = ["https://*.blockanalitica.com"]

# Application definition

INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "rest_framework",
    "django_celery_beat",
    "ajna.apps.AjnaConfig",
    "corsheaders",
]

MIDDLEWARE = [
    "ajna.middleware.HealthCheckMiddleware",
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env("AJNA_DB_NAME", default=""),
        "USER": env("AJNA_DB_USER", default=""),
        "PASSWORD": env("AJNA_DB_PASSWORD", default=""),
        "HOST": env("AJNA_DB_HOST", default=""),
        "PORT": env("AJNA_DB_PORT", default="5432"),
    }
}


# Celery configuration options
CELERY_BROKER_URL = "redis://{}:{}/1".format(
    env("AJNA_REDIS_HOST", default=None),
    env("AJNA_REDIS_PORT", default="6379"),
)
CELERY_TASK_DEFAULT_QUEUE = "default"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 10 * 60
CELERY_TASK_ALWAYS_EAGER = False
CELERY_WORKER_MAX_TASKS_PER_CHILD = env.int(
    "CELERY_WORKER_MAX_TASKS_PER_CHILD", default=1000
)
CELERY_WORKER_PREFETCH_MULTIPLIER = env.int(
    "CELERY_WORKER_PREFETCH_MULTIPLIER", default=1
)
CELERY_WORKER_MAX_MEMORY_PER_CHILD = env.int(
    "CELERY_WORKER_MAX_MEMORY_PER_CHILD",
    default=256000,  # 256MB
)


CELERY_IMPORTS = [
    "ajna.v2.ethereum.tasks",
    "ajna.v3.base.tasks",
    "ajna.v3.arbitrum.tasks",
    "ajna.v3.optimism.tasks",
    "ajna.v3.polygon.tasks",
    # "ajna.v4.goerli.tasks",
    "ajna.v4.ethereum.tasks",
    "ajna.v4.base.tasks",
    "ajna.v4.arbitrum.tasks",
    "ajna.v4.optimism.tasks",
    "ajna.v4.polygon.tasks",
    # "ajna.v4.blast.tasks",
]

# django-celery-beat configuration options
DJANGO_CELERY_BEAT_TZ_AWARE = False


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = False

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
STATIC_URL = "static/"
STATICFILES_DIRS = []
STATIC_ROOT = BASE_DIR / "static"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

sentry_sdk.init(
    integrations=[DjangoIntegration()],
    send_default_pii=True,
    environment=env("AJNA_ENVIRONMENT", default=None),
    traces_sample_rate=float(env("SENTRY_TRACES_SAMPLE_RATE", default=0.0)),
)
ignore_logger("django.security.DisallowedHost")

STATSD_HOST = env("STATSD_HOST", default="localhost")
STATSD_PORT = env("STATSD_PORT", default=8125)
STATSD_PREFIX = env("STATSD_PREFIX", default=None)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": (
                "[%(asctime)s] %(name)s {%(module)s:%(lineno)d} PID=%(process)d "
                "%(levelname)s - %(message)s"
            )
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "standard",
        },
    },
    "loggers": {
        "django": {
            "propagate": True,
            "level": env("DJANGO_LOG_LEVEL", default="INFO"),
        },
        "django_bulk_load": {
            "propagate": True,
            "level": "WARNING",
        },
        "ajna": {
            "propagate": True,
            "level": env("AJNA_LOG_LEVEL", default="INFO"),
        },
        "": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://{}:{}/{}".format(
            env("AJNA_REDIS_HOST", default=None),
            env("AJNA_REDIS_PORT", default="6379"),
            env("AJNA_REDIS_DB", default="0"),
        ),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PARSER_CLASS": "redis.connection._HiredisParser",
            "IGNORE_EXCEPTIONS": True,
            "SOCKET_CONNECT_TIMEOUT": 1,
            "SOCKET_TIMEOUT": 1,
        },
    }
}

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "ajna.renderer.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ]
}

CACHE_MIDDLEWARE_SECONDS = env.int("CACHE_MIDDLEWARE_SECONDS", default=10)

SUBGRAPH_ENDPOINT_GOERLI = env("SUBGRAPH_ENDPOINT", default="")
SUBGRAPH_ENDPOINT_MAINNET = env("SUBGRAPH_ENDPOINT_MAINNET", default="")
GOERLI_NODE = env("GOERLI_NODE", default="")
ETHEREUM_NODE = env("ETHEREUM_NODE", default="")
BASE_NODE = env("BASE_NODE", default="")
ARBITRUM_NODE = env("ARBITRUM_NODE", default="")
POLYGON_NODE = env("POLYGON_NODE", default="")
OPTIMISM_NODE = env("OPTIMISM_NODE", default="")
BLAST_NODE = env("BLAST_NODE", default="")

ETHERSCAN_API_KEY = env("ETHERSCAN_API_KEY", default="")
ARBISCAN_API_KEY = env("ARBISCAN_API_KEY", default="")
BASESCAN_API_KEY = env("BASESCAN_API_KEY", default="")
OPTIMISTIC_ETHERSCAN_API_KEY = env("OPTIMISTIC_ETHERSCAN_API_KEY", default="")
POLYGONSCAN_API_KEY = env("POLYGONSCAN_API_KEY", default="")
BLASTSCAN_API_KEY = env("BLASTSCAN_API_KEY", default="")
