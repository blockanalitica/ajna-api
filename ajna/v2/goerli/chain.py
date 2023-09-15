from chain_harvester.networks.ethereum.goerli import EthereumGoerliChain
from django.conf import settings

from ajna.chain import AjnaChainMixin

from . import models

MODEL_MAP = {
    "pool": models.V2GoerliPool,
    "token": models.V2GoerliToken,
    "pool_snapshot": models.V2GoerliPoolSnapshot,
    "bucket": models.V2GoerliBucket,
    "price_feed": models.V2GoerliPriceFeed,
    "liqudation_auction": models.V2GoerliLiquidationAuction,
    "pool_volume_snapshot": models.V2GoerliPoolVolumeSnapshot,
    "grant_proposal": models.V2GoerliGrantProposal,
    "pool_event": models.V2GoerliPoolEvent,
    "current_wallet_position": models.V2GoerliCurrentWalletPoolPosition,
    "wallet_position": models.V2GoerliWalletPoolPosition,
    "wallet_bucket_state": models.V2GoerliWalletPoolBucketState,
    "bucket_state": models.V2GoerliPoolBucketState,
    "wallet": models.V2GoerliWallet,
}


class GoerliModels:
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)


class Goerli(AjnaChainMixin, EthereumGoerliChain):
    def __init__(self, *args, **kwargs):
        super().__init__(
            rpc=settings.GOERLI_NODE,
            api_key=settings.ETHERSCAN_API_KEY,
            step=50000,
            *args,
            **kwargs,
        )
        self.pool_info_address = "0xBB61407715cDf92b2784E9d2F1675c4B8505cBd8"
        self.erc20_pool_abi_contract = "0x6e173d30ccd286577ed7eeedc0cd4a6caeb7a669"
        self.erc20_pool_factory_address = "0x01Da8a85A5B525D476cA2b51e44fe7087fFafaFF"

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)

        # Celery task workaround
        # Since we need to access specific tasks sometimes (ethereum, goerli,...) we've
        # attached them to chain, since chain object is the base of almost everything
        from . import tasks

        self.celery_tasks = tasks
