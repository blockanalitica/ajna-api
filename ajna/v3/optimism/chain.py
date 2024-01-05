import logging

from chain_harvester.networks.optimism.mainnet import OptimismMainnetChain
from django.conf import settings

from ajna.chain import AjnaChainMixin

from . import models

log = logging.getLogger(__name__)


MODEL_MAP = {
    "pool": models.V3OptimismPool,
    "token": models.V3OptimismToken,
    "pool_snapshot": models.V3OptimismPoolSnapshot,
    "bucket": models.V3OptimismBucket,
    "price_feed": models.V3OptimismPriceFeed,
    "pool_volume_snapshot": models.V3OptimismPoolVolumeSnapshot,
    "pool_event": models.V3OptimismPoolEvent,
    "current_wallet_position": models.V3OptimismCurrentWalletPoolPosition,
    "wallet_position": models.V3OptimismWalletPoolPosition,
    "wallet_bucket_state": models.V3OptimismWalletPoolBucketState,
    "bucket_state": models.V3OptimismPoolBucketState,
    "wallet": models.V3OptimismWallet,
    "notification": models.V3OptimismNotification,
    "auction": models.V3OptimismAuction,
    "auction_kick": models.V3OptimismAuctionKick,
    "auction_take": models.V3OptimismAuctionTake,
    "auction_bucket_take": models.V3OptimismAuctionBucketTake,
    "auction_settle": models.V3OptimismAuctionSettle,
    "auction_auction_settle": models.V3OptimismAuctionAuctionSettle,
    "auction_auction_nft_settle": models.V3OptimismAuctionAuctionNFTSettle,
    "reserve_auction": models.V3OptimismReserveAuction,
    "reserve_auction_kick": models.V3OptimismReserveAuctionKick,
    "reserve_auction_take": models.V3OptimismReserveAuctionTake,
    "grant_distribution_period": models.V3OptimismGrantDistributionPeriod,
    "grant_proposal": models.V3OptimismGrantProposal,
    "grant_event": models.V3OptimismGrantEvent,
}


class OptimismModels:
    def __init__(self):
        super().__init__()

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)


class Optimism(AjnaChainMixin, OptimismMainnetChain):
    def __init__(self):
        super().__init__(
            rpc=settings.OPTIMISM_NODE,
            api_key=settings.OPTIMISTIC_ETHERSCAN_API_KEY,
            step=50000,
        )
        self.unique_key = "v3_optimism"

        self.pool_info_address = "0x6293C850837d617DE66ddf7d8744E2BDbD913A90"
        self.erc20_pool_abi_contract = ""
        self.erc20_pool_factory_address = "0x43cD60250CBBC0C22663438dcf644F5162988C06"
        self.erc20_pool_factory_start_block = 114432276
        self.erc721_pool_abi_contract = ""
        self.erc721_pool_factory_address = "0x7F4bE0828dC1523A27f20a597d1F1bB4b5134123"
        self.erc721_pool_factory_start_block = 114432276
        self.grant_fund_address = ""
        self.grant_fund_start_block = 0

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)

        # Celery task workaround
        # Since we need to access specific tasks sometimes (ethereum, Base,...) we've
        # attached them to chain, since chain object is the base of almost everything
        from . import tasks

        self.celery_tasks = tasks
