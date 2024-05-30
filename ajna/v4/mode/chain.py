import logging

from chain_harvester.networks.mode.mainnet import ModeMainnetChain
from django.conf import settings

from ajna.chain import AjnaChainMixin

from . import models

log = logging.getLogger(__name__)


MODEL_MAP = {
    "pool": models.V4ModePool,
    "token": models.V4ModeToken,
    "pool_snapshot": models.V4ModePoolSnapshot,
    "bucket": models.V4ModeBucket,
    "price_feed": models.V4ModePriceFeed,
    "pool_volume_snapshot": models.V4ModePoolVolumeSnapshot,
    "pool_event": models.V4ModePoolEvent,
    "current_wallet_position": models.V4ModeCurrentWalletPoolPosition,
    "wallet_position": models.V4ModeWalletPoolPosition,
    "wallet_bucket_state": models.V4ModeWalletPoolBucketState,
    "bucket_state": models.V4ModePoolBucketState,
    "wallet": models.V4ModeWallet,
    "notification": models.V4ModeNotification,
    "auction": models.V4ModeAuction,
    "auction_kick": models.V4ModeAuctionKick,
    "auction_take": models.V4ModeAuctionTake,
    "auction_bucket_take": models.V4ModeAuctionBucketTake,
    "auction_settle": models.V4ModeAuctionSettle,
    "auction_auction_settle": models.V4ModeAuctionAuctionSettle,
    "auction_auction_nft_settle": models.V4ModeAuctionAuctionNFTSettle,
    "reserve_auction": models.V4ModeReserveAuction,
    "reserve_auction_kick": models.V4ModeReserveAuctionKick,
    "reserve_auction_take": models.V4ModeReserveAuctionTake,
    "activity_snapshot": models.V4ModeActivitySnapshot,
}


class ModeModels:
    def __init__(self):
        super().__init__()

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)


class Mode(AjnaChainMixin, ModeMainnetChain):
    def __init__(self):
        super().__init__(
            rpc=settings.MODE_NODE,
            api_key="don't need",
            step=10000,
        )
        self.unique_key = "v4_mode"

        self.pool_info_address = "0x6EF483c3653907c19bDD4300087e481551880c60"
        self.erc20_pool_abi_contract = ""
        self.erc20_pool_factory_address = "0x62Cf5d9075D1d6540A6c7Fa836162F01a264115A"
        self.erc20_pool_factory_start_block = 7137311
        self.erc721_pool_abi_contract = ""
        self.erc721_pool_factory_address = "0x2189eC0743e36f2CB51BEdaf089d686BC0996e03"
        self.erc721_pool_factory_start_block = 7137312
        self.grant_fund_address = ""
        self.grant_fund_start_block = 0

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)

        # Celery task workaround
        # Since we need to access specific tasks sometimes (ethereum, base,...) we've
        # attached them to chain, since chain object is the base of almost everything
        from . import tasks

        self.celery_tasks = tasks
