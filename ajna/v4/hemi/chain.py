import logging

from chain_harvester.networks.hemi.mainnet import HemiMainnetChain
from django.conf import settings

from ajna.chain import AjnaChainMixin

from . import models

log = logging.getLogger(__name__)


MODEL_MAP = {
    "pool": models.V4HemiPool,
    "token": models.V4HemiToken,
    "pool_snapshot": models.V4HemiPoolSnapshot,
    "bucket": models.V4HemiBucket,
    "price_feed": models.V4HemiPriceFeed,
    "pool_volume_snapshot": models.V4HemiPoolVolumeSnapshot,
    "pool_event": models.V4HemiPoolEvent,
    "current_wallet_position": models.V4HemiCurrentWalletPoolPosition,
    "wallet_position": models.V4HemiWalletPoolPosition,
    "wallet_bucket_state": models.V4HemiWalletPoolBucketState,
    "bucket_state": models.V4HemiPoolBucketState,
    "wallet": models.V4HemiWallet,
    "notification": models.V4HemiNotification,
    "auction": models.V4HemiAuction,
    "auction_kick": models.V4HemiAuctionKick,
    "auction_take": models.V4HemiAuctionTake,
    "auction_bucket_take": models.V4HemiAuctionBucketTake,
    "auction_settle": models.V4HemiAuctionSettle,
    "auction_auction_settle": models.V4HemiAuctionAuctionSettle,
    "auction_auction_nft_settle": models.V4HemiAuctionAuctionNFTSettle,
    "reserve_auction": models.V4HemiReserveAuction,
    "reserve_auction_kick": models.V4HemiReserveAuctionKick,
    "reserve_auction_take": models.V4HemiReserveAuctionTake,
    "activity_snapshot": models.V4HemiActivitySnapshot,
}


class HemiModels:
    def __init__(self):
        super().__init__()

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)


class Hemi(AjnaChainMixin, HemiMainnetChain):
    def __init__(self):
        super().__init__(
            rpc=settings.HEMI_NODE,
            step=1_000_000,
        )
        self.unique_key = "v4_hemi"

        self.pool_info_address = "0xab57F608c37879360D622C32C6eF3BBa79AA667D"
        self.erc20_pool_abi_contract = "0xBCA61135bf839D9e6864877D2F07F6C82A1C7614"
        self.erc20_pool_factory_address = "0xE47b3D287Fc485A75146A59d459EC8CD0F8E5021"
        self.erc20_pool_factory_start_block = 363925
        self.erc721_pool_abi_contract = "0xd7b29C42CB5B3e350c19d481fEE46171f9C20557"
        self.erc721_pool_factory_address = "0x3E0126d3B10596b7E13e42E34B7cBD0E9735e4c0"
        self.erc721_pool_factory_start_block = 363926
        self.grant_fund_address = ""
        self.grant_fund_start_block = 0

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)

        # Celery task workaround
        # Since we need to access specific tasks sometimes (ethereum, Base,...) we've
        # attached them to chain, since chain object is the base of almost everything
        from . import tasks

        self.celery_tasks = tasks
