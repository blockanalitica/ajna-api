from config.settings.base import *  # noqa

DEBUG = True

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

CELERY_ALWAYS_EAGER = True

SUBGRAPH_ENDPOINT_GOERLI = "http://localhost:8000/subgraph/"

GOERLI_NODE = "dummy-goerli"
ETHEREUM_NODE = "dummy-ethereum"
ETHERSCAN_API_KEY = "no-key"
