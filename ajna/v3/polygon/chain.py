import logging

from chain_harvester.networks.polygon.mainnet import PolygonMainnetChain
from django.conf import settings

from ajna.chain import AjnaChainMixin

from . import models

log = logging.getLogger(__name__)


MODEL_MAP = {
    "pool": models.V3PolygonPool,
    "token": models.V3PolygonToken,
    "pool_snapshot": models.V3PolygonPoolSnapshot,
    "bucket": models.V3PolygonBucket,
    "price_feed": models.V3PolygonPriceFeed,
    "pool_volume_snapshot": models.V3PolygonPoolVolumeSnapshot,
    "pool_event": models.V3PolygonPoolEvent,
    "current_wallet_position": models.V3PolygonCurrentWalletPoolPosition,
    "wallet_position": models.V3PolygonWalletPoolPosition,
    "wallet_bucket_state": models.V3PolygonWalletPoolBucketState,
    "bucket_state": models.V3PolygonPoolBucketState,
    "wallet": models.V3PolygonWallet,
    "notification": models.V3PolygonNotification,
    "auction": models.V3PolygonAuction,
    "auction_kick": models.V3PolygonAuctionKick,
    "auction_take": models.V3PolygonAuctionTake,
    "auction_bucket_take": models.V3PolygonAuctionBucketTake,
    "auction_settle": models.V3PolygonAuctionSettle,
    "auction_auction_settle": models.V3PolygonAuctionAuctionSettle,
    "auction_auction_nft_settle": models.V3PolygonAuctionAuctionNFTSettle,
    "reserve_auction": models.V3PolygonReserveAuction,
    "reserve_auction_kick": models.V3PolygonReserveAuctionKick,
    "reserve_auction_take": models.V3PolygonReserveAuctionTake,
    "grant_distribution_period": models.V3PolygonGrantDistributionPeriod,
    "grant_proposal": models.V3PolygonGrantProposal,
    "grant_event": models.V3PolygonGrantEvent,
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
            api_key=settings.POLYGONSCAN_API_KEY,
            step=50000,
        )
        self.unique_key = "v3_polygon"

        self.pool_info_address = "0x68C75c041BC36AFdce7cae2578BEe31a24888885"
        self.erc20_pool_abi_contract = "0x0df2A72fa7Ba0F6306e84247be063800f5E1279d"
        self.erc20_pool_factory_address = "0x3D6b8B4a2AEC46961AE337F4A9EBbf283aA482AA"
        self.erc20_pool_factory_start_block = 51974039
        self.erc721_pool_abi_contract = "0x833f2dAa69D582c81E130413dF4402b7fD4a670b"
        self.erc721_pool_factory_address = "0x1D705aa62DC4E95fd8A473476aF619AD0853E560"
        self.erc721_pool_factory_start_block = 51974039
        self.grant_fund_address = ""
        self.grant_fund_start_block = 0

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)

        # Celery task workaround
        # Since we need to access specific tasks sometimes (ethereum, Base,...) we've
        # attached them to chain, since chain object is the base of almost everything
        from . import tasks

        self.celery_tasks = tasks
