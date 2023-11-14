from chain_harvester.networks.ethereum.goerli import EthereumGoerliChain
from django.conf import settings

from ajna.chain import AjnaChainMixin

from . import models

MODEL_MAP = {
    "pool": models.V3GoerliPool,
    "token": models.V3GoerliToken,
    "pool_snapshot": models.V3GoerliPoolSnapshot,
    "bucket": models.V3GoerliBucket,
    "price_feed": models.V3GoerliPriceFeed,
    "pool_volume_snapshot": models.V3GoerliPoolVolumeSnapshot,
    "pool_event": models.V3GoerliPoolEvent,
    "current_wallet_position": models.V3GoerliCurrentWalletPoolPosition,
    "wallet_position": models.V3GoerliWalletPoolPosition,
    "wallet_bucket_state": models.V3GoerliWalletPoolBucketState,
    "bucket_state": models.V3GoerliPoolBucketState,
    "wallet": models.V3GoerliWallet,
    "notification": models.V3GoerliNotification,
    "auction": models.V3GoerliAuction,
    "auction_kick": models.V3GoerliAuctionKick,
    "auction_take": models.V3GoerliAuctionTake,
    "auction_bucket_take": models.V3GoerliAuctionBucketTake,
    "auction_settle": models.V3GoerliAuctionSettle,
    "auction_auction_settle": models.V3GoerliAuctionAuctionSettle,
    "auction_auction_nft_settle": models.V3GoerliAuctionAuctionNFTSettle,
    "reserve_auction": models.V3GoerliReserveAuction,
    "reserve_auction_kick": models.V3GoerliReserveAuctionKick,
    "reserve_auction_take": models.V3GoerliReserveAuctionTake,
    "grant_distribution_period": models.V3GoerliGrantDistributionPeriod,
    "grant_proposal": models.V3GoerliGrantProposal,
    "grant_event": models.V3GoerliGrantEvent,
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
        self.unique_key = "v3_goerli"

        self.pool_info_address = "0x08F304cBeA7FAF48C93C27ae1305E220913a571d"
        self.erc20_pool_abi_contract = "0x5a4fb4f6a83282d62c3fc87c4dfe9a2849d987e9"
        self.erc20_pool_factory_address = "0x14F2474fB5ea9DF82059053c4F85A8C803Ab10C9"
        self.erc20_pool_factory_start_block = 9888337
        self.erc721_pool_abi_contract = "0x7c79c719081d987678b1cfab5f95b48f3cec55b2"
        self.erc721_pool_factory_address = "0xb0d1c875B240EE9f6C2c3284a31b10f1EC6De7d2"
        self.erc721_pool_factory_start_block = 9888337
        self.grant_fund_address = "0x17C7eb98aD29c8C07C2842C4B64342142C405aF4"
        self.grant_fund_start_block = 9929353

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)

        # Celery task workaround
        # Since we need to access specific tasks sometimes (ethereum, goerli,...) we've
        # attached them to chain, since chain object is the base of almost everything
        from . import tasks

        self.celery_tasks = tasks
