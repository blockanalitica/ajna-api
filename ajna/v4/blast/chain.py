import logging

from chain_harvester.networks.blast.mainnet import BlastMainnetChain
from django.conf import settings

from ajna.chain import AjnaChainMixin

from . import models

log = logging.getLogger(__name__)


MODEL_MAP = {
    "pool": models.V4BlastPool,
    "token": models.V4BlastToken,
    "pool_snapshot": models.V4BlastPoolSnapshot,
    "bucket": models.V4BlastBucket,
    "price_feed": models.V4BlastPriceFeed,
    "pool_volume_snapshot": models.V4BlastPoolVolumeSnapshot,
    "pool_event": models.V4BlastPoolEvent,
    "current_wallet_position": models.V4BlastCurrentWalletPoolPosition,
    "wallet_position": models.V4BlastWalletPoolPosition,
    "wallet_bucket_state": models.V4BlastWalletPoolBucketState,
    "bucket_state": models.V4BlastPoolBucketState,
    "wallet": models.V4BlastWallet,
    "notification": models.V4BlastNotification,
    "auction": models.V4BlastAuction,
    "auction_kick": models.V4BlastAuctionKick,
    "auction_take": models.V4BlastAuctionTake,
    "auction_bucket_take": models.V4BlastAuctionBucketTake,
    "auction_settle": models.V4BlastAuctionSettle,
    "auction_auction_settle": models.V4BlastAuctionAuctionSettle,
    "auction_auction_nft_settle": models.V4BlastAuctionAuctionNFTSettle,
    "reserve_auction": models.V4BlastReserveAuction,
    "reserve_auction_kick": models.V4BlastReserveAuctionKick,
    "reserve_auction_take": models.V4BlastReserveAuctionTake,
}


class BlastModels:
    def __init__(self):
        super().__init__()

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)


class Blast(AjnaChainMixin, BlastMainnetChain):
    def __init__(self):
        super().__init__(
            rpc=settings.BLAST_NODE,
            api_key=settings.BLASTSCAN_API_KEY,
            step=10000,
        )
        self.unique_key = "v4_blast"

        self.pool_info_address = "0x6aF0363e5d2ddab4471f31Fe2834145Aea1E55Ee"
        self.erc20_pool_abi_contract = "0x2add6E4646dC2C9f298c037b19f11B67F0508ceD"
        self.erc20_pool_factory_address = "0xcfCB7fb8c13c7bEffC619c3413Ad349Cbc6D5c91"
        self.erc20_pool_factory_start_block = 436725
        self.erc721_pool_abi_contract = "0x4047c479d0189b1edbe485a9d79cc26e4dd04bc8"
        self.erc721_pool_factory_address = "0x6C046C4b072404ce7865a7c317b432B5e269822A"
        self.erc721_pool_factory_start_block = 436725
        self.grant_fund_address = ""
        self.grant_fund_start_block = 0

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)

        # Celery task workaround
        # Since we need to access specific tasks sometimes (ethereum, base,...) we've
        # attached them to chain, since chain object is the base of almost everything
        from . import tasks

        self.celery_tasks = tasks
