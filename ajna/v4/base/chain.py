import logging

from chain_harvester.networks.base.mainnet import BaseMainnetChain
from django.conf import settings

from ajna.chain import AjnaChainMixin

from . import models

log = logging.getLogger(__name__)


MODEL_MAP = {
    "pool": models.V4BasePool,
    "token": models.V4BaseToken,
    "pool_snapshot": models.V4BasePoolSnapshot,
    "bucket": models.V4BaseBucket,
    "price_feed": models.V4BasePriceFeed,
    "pool_volume_snapshot": models.V4BasePoolVolumeSnapshot,
    "pool_event": models.V4BasePoolEvent,
    "current_wallet_position": models.V4BaseCurrentWalletPoolPosition,
    "wallet_position": models.V4BaseWalletPoolPosition,
    "wallet_bucket_state": models.V4BaseWalletPoolBucketState,
    "bucket_state": models.V4BasePoolBucketState,
    "wallet": models.V4BaseWallet,
    "notification": models.V4BaseNotification,
    "auction": models.V4BaseAuction,
    "auction_kick": models.V4BaseAuctionKick,
    "auction_take": models.V4BaseAuctionTake,
    "auction_bucket_take": models.V4BaseAuctionBucketTake,
    "auction_settle": models.V4BaseAuctionSettle,
    "auction_auction_settle": models.V4BaseAuctionAuctionSettle,
    "auction_auction_nft_settle": models.V4BaseAuctionAuctionNFTSettle,
    "reserve_auction": models.V4BaseReserveAuction,
    "reserve_auction_kick": models.V4BaseReserveAuctionKick,
    "reserve_auction_take": models.V4BaseReserveAuctionTake,
    "activity_snapshot": models.V4BaseActivitySnapshot,
}


class BaseModels:
    def __init__(self):
        super().__init__()

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)


class Base(AjnaChainMixin, BaseMainnetChain):
    def __init__(self):
        super().__init__(
            rpc=settings.BASE_NODE,
            api_key=settings.BASESCAN_API_KEY,
            step=50000,
        )
        self.unique_key = "v4_base"

        self.pool_info_address = "0x97fa9b0909C238D170C1ab3B5c728A3a45BBEcBa"
        self.erc20_pool_abi_contract = "0x6d8aD935511464C0343916AE8DC5641e9351288b"
        self.erc20_pool_factory_address = "0x214f62B5836D83f3D6c4f71F174209097B1A779C"
        self.erc20_pool_factory_start_block = 9367126
        self.erc721_pool_abi_contract = "0x32036492Ae5FDA5Cb46D79f1b048816518e3ec7c"
        self.erc721_pool_factory_address = "0xeefEC5d1Cc4bde97279d01D88eFf9e0fEe981769"
        self.erc721_pool_factory_start_block = 9367129
        self.grant_fund_address = ""
        self.grant_fund_start_block = 0

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)

        # Celery task workaround
        # Since we need to access specific tasks sometimes (ethereum, Base,...) we've
        # attached them to chain, since chain object is the base of almost everything
        from . import tasks

        self.celery_tasks = tasks
