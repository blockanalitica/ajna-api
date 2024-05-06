from config.settings.base import *  # noqa: F403

DEBUG = True

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

CELERY_ALWAYS_EAGER = True

SUBGRAPH_ENDPOINT_GOERLI = "http://localhost:8000/subgraph/"

SUBGRAPH_ENDPOINT_GOERLI = "http://subgraph:8000/goerli/"
SUBGRAPH_ENDPOINT_MAINNET = "http://subgraph:8000/mainnet/"

GOERLI_NODE = "http://eth_node/goerli"
ETHEREUM_NODE = "http://eth_node/mainnet"
BASE_NODE = "http://eth_node/base"
ARBITRUM_NODE = "http://eth_node/arbitrum"
POLYGON_NODE = "http://eth_node/polygon"
OPTIMISM_NODE = "http://eth_node/optimism"

ETHERSCAN_API_KEY = "no-key"
ARBISCAN_API_KEY = "no-key"
BASESCAN_API_KEY = "no-key"
OPTIMISTIC_ETHERSCAN_API_KEY = "no-key"
POLYGONSCAN_API_KEY = "no-key"
