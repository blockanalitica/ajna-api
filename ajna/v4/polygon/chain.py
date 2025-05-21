import logging

from chain_harvester.networks.polygon.mainnet import PolygonMainnetChain
from django.conf import settings

from ajna.chain import AjnaChainMixin

from . import models

log = logging.getLogger(__name__)


MODEL_MAP = {
    "pool": models.V4PolygonPool,
    "token": models.V4PolygonToken,
    "pool_snapshot": models.V4PolygonPoolSnapshot,
    "bucket": models.V4PolygonBucket,
    "price_feed": models.V4PolygonPriceFeed,
    "pool_volume_snapshot": models.V4PolygonPoolVolumeSnapshot,
    "pool_event": models.V4PolygonPoolEvent,
    "current_wallet_position": models.V4PolygonCurrentWalletPoolPosition,
    "wallet_position": models.V4PolygonWalletPoolPosition,
    "wallet_bucket_state": models.V4PolygonWalletPoolBucketState,
    "bucket_state": models.V4PolygonPoolBucketState,
    "wallet": models.V4PolygonWallet,
    "notification": models.V4PolygonNotification,
    "auction": models.V4PolygonAuction,
    "auction_kick": models.V4PolygonAuctionKick,
    "auction_take": models.V4PolygonAuctionTake,
    "auction_bucket_take": models.V4PolygonAuctionBucketTake,
    "auction_settle": models.V4PolygonAuctionSettle,
    "auction_auction_settle": models.V4PolygonAuctionAuctionSettle,
    "auction_auction_nft_settle": models.V4PolygonAuctionAuctionNFTSettle,
    "reserve_auction": models.V4PolygonReserveAuction,
    "reserve_auction_kick": models.V4PolygonReserveAuctionKick,
    "reserve_auction_take": models.V4PolygonReserveAuctionTake,
    "activity_snapshot": models.V4PolygonActivitySnapshot,
}


class PolygonModels:
    def __init__(self):
        super().__init__()

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)


class Polygon(AjnaChainMixin, PolygonMainnetChain):
    def __init__(self):
        super().__init__(
            rpc=settings.POLYGON_NODE,
            etherscan_api_key=settings.ETHERSCAN_API_KEY,
            step=50000,
        )
        self.unique_key = "v4_polygon"

        self.pool_info_address = "0x519021054846cd3D9883359B593B5ED3058Fbe9f"
        self.erc20_pool_abi_contract = "0x6D75CB35DA097ffeE341B5E671D8aFEb7d9742Ce"
        self.erc20_pool_factory_address = "0x1f172F881eBa06Aa7a991651780527C173783Cf6"
        self.erc20_pool_factory_start_block = 52443388
        self.erc721_pool_abi_contract = "0xB9eFBac08F779903D09C4222f20253A8259317fC"
        self.erc721_pool_factory_address = "0x8B7f874D15c25BeCC4F7c1906b3677533fe60A6e"
        self.erc721_pool_factory_start_block = 52443388
        self.grant_fund_address = ""
        self.grant_fund_start_block = 0

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)

        # Celery task workaround
        # Since we need to access specific tasks sometimes (ethereum, Base,...) we've
        # attached them to chain, since chain object is the base of almost everything
        from . import tasks

        self.celery_tasks = tasks
