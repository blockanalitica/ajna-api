import logging

from chain_harvester.networks.optimism.mainnet import OptimismMainnetChain
from django.conf import settings

from ajna.chain import AjnaChainMixin

from . import models

log = logging.getLogger(__name__)


MODEL_MAP = {
    "pool": models.V4OptimismPool,
    "token": models.V4OptimismToken,
    "pool_snapshot": models.V4OptimismPoolSnapshot,
    "bucket": models.V4OptimismBucket,
    "price_feed": models.V4OptimismPriceFeed,
    "pool_volume_snapshot": models.V4OptimismPoolVolumeSnapshot,
    "pool_event": models.V4OptimismPoolEvent,
    "current_wallet_position": models.V4OptimismCurrentWalletPoolPosition,
    "wallet_position": models.V4OptimismWalletPoolPosition,
    "wallet_bucket_state": models.V4OptimismWalletPoolBucketState,
    "bucket_state": models.V4OptimismPoolBucketState,
    "wallet": models.V4OptimismWallet,
    "notification": models.V4OptimismNotification,
    "auction": models.V4OptimismAuction,
    "auction_kick": models.V4OptimismAuctionKick,
    "auction_take": models.V4OptimismAuctionTake,
    "auction_bucket_take": models.V4OptimismAuctionBucketTake,
    "auction_settle": models.V4OptimismAuctionSettle,
    "auction_auction_settle": models.V4OptimismAuctionAuctionSettle,
    "auction_auction_nft_settle": models.V4OptimismAuctionAuctionNFTSettle,
    "reserve_auction": models.V4OptimismReserveAuction,
    "reserve_auction_kick": models.V4OptimismReserveAuctionKick,
    "reserve_auction_take": models.V4OptimismReserveAuctionTake,
    "activity_snapshot": models.V4OptimismActivitySnapshot,
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
        self.unique_key = "v4_optimism"

        self.pool_info_address = "0xdE6C8171b5b971F71C405631f4e0568ed8491aaC"
        self.erc20_pool_abi_contract = "0xa353e6dfd41Dc98ee4000f1B8cA7f59971712b6e"
        self.erc20_pool_factory_address = "0x609C4e8804fafC07c96bE81A8a98d0AdCf2b7Dfa"
        self.erc20_pool_factory_start_block = 114962902
        self.erc721_pool_abi_contract = "0xf6ecE51494edbbF9cE5B85a19AD739E5Ff29FE8F"
        self.erc721_pool_factory_address = "0xAAa20ba75A7ed4Fa895E4659861448a828fa6E48"
        self.erc721_pool_factory_start_block = 114962905
        self.grant_fund_address = ""
        self.grant_fund_start_block = 0

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)

        # Celery task workaround
        # Since we need to access specific tasks sometimes (ethereum, Base,...) we've
        # attached them to chain, since chain object is the base of almost everything
        from . import tasks

        self.celery_tasks = tasks
