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
    "pool_volume_snapshot": models.V2GoerliPoolVolumeSnapshot,
    "pool_event": models.V2GoerliPoolEvent,
    "current_wallet_position": models.V2GoerliCurrentWalletPoolPosition,
    "wallet_position": models.V2GoerliWalletPoolPosition,
    "wallet_bucket_state": models.V2GoerliWalletPoolBucketState,
    "bucket_state": models.V2GoerliPoolBucketState,
    "wallet": models.V2GoerliWallet,
    "notification": models.V2GoerliNotification,
    "auction": models.V2GoerliAuction,
    "auction_kick": models.V2GoerliAuctionKick,
    "auction_take": models.V2GoerliAuctionTake,
    "auction_bucket_take": models.V2GoerliAuctionBucketTake,
    "auction_settle": models.V2GoerliAuctionSettle,
    "auction_auction_settle": models.V2GoerliAuctionAuctionSettle,
    "grant_distribution_period": models.V2GoerliGrantDistributionPeriod,
    "grant_proposal": models.V2GoerliGrantProposal,
    "grant_event": models.V2GoerliGrantEvent,
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
        self.unique_key = "v2_goerli"

        self.pool_info_address = "0xBB61407715cDf92b2784E9d2F1675c4B8505cBd8"
        self.erc20_pool_abi_contract = "0x6e173d30ccd286577ed7eeedc0cd4a6caeb7a669"
        self.erc20_pool_factory_address = "0x01Da8a85A5B525D476cA2b51e44fe7087fFafaFF"
        self.erc20_pool_factory_start_block = 9289397
        self.erc721_pool_abi_contract = "0x74a48dd965841d28ef062b52ce2dda49c1a33c46"
        self.erc721_pool_factory_address = "0x37048D43A65748409B04f4051eEd9480BEf68c82"
        self.erc721_pool_factory_start_block = 9289398
        self.grant_fund_address = "0x881b4dFF6C72babA6f5eA60f34A61410c1EA1ec2"
        self.grant_fund_start_block = 9297080

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)

        # Celery task workaround
        # Since we need to access specific tasks sometimes (ethereum, goerli,...) we've
        # attached them to chain, since chain object is the base of almost everything
        from . import tasks

        self.celery_tasks = tasks
