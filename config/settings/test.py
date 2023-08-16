from config.settings.base import *  # noqa

DEBUG = True

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

CELERY_ALWAYS_EAGER = True

SUBGRAPH_ENDPOINT_GOERLI = "http://subgraph:8000/goerli/"
SUBGRAPH_ENDPOINT_MAINNET = "http://subgraph:8000/mainnet/"
GOERLI_NODE = "http://eth_node/goerli"
ETHEREUM_NODE = "http://eth_node/mainnet"
