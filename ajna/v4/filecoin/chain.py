import logging

from chain_harvester.networks.filecoin.mainnet import FilecoinMainnetChain
from django.conf import settings

from ajna.chain import AjnaChainMixin

from . import models

log = logging.getLogger(__name__)


MODEL_MAP = {
    "pool": models.V4FilecoinPool,
    "token": models.V4FilecoinToken,
    "pool_snapshot": models.V4FilecoinPoolSnapshot,
    "bucket": models.V4FilecoinBucket,
    "price_feed": models.V4FilecoinPriceFeed,
    "pool_volume_snapshot": models.V4FilecoinPoolVolumeSnapshot,
    "pool_event": models.V4FilecoinPoolEvent,
    "current_wallet_position": models.V4FilecoinCurrentWalletPoolPosition,
    "wallet_position": models.V4FilecoinWalletPoolPosition,
    "wallet_bucket_state": models.V4FilecoinWalletPoolBucketState,
    "bucket_state": models.V4FilecoinPoolBucketState,
    "wallet": models.V4FilecoinWallet,
    "notification": models.V4FilecoinNotification,
    "auction": models.V4FilecoinAuction,
    "auction_kick": models.V4FilecoinAuctionKick,
    "auction_take": models.V4FilecoinAuctionTake,
    "auction_bucket_take": models.V4FilecoinAuctionBucketTake,
    "auction_settle": models.V4FilecoinAuctionSettle,
    "auction_auction_settle": models.V4FilecoinAuctionAuctionSettle,
    "auction_auction_nft_settle": models.V4FilecoinAuctionAuctionNFTSettle,
    "reserve_auction": models.V4FilecoinReserveAuction,
    "reserve_auction_kick": models.V4FilecoinReserveAuctionKick,
    "reserve_auction_take": models.V4FilecoinReserveAuctionTake,
}


class FilecoinModels:
    def __init__(self):
        super().__init__()

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)


class Filecoin(AjnaChainMixin, FilecoinMainnetChain):
    def __init__(self):
        super().__init__(
            rpc=settings.FILECOIN_NODE,
            api_key="don't need",
            step=2880,
        )
        self.unique_key = "v4_filecoin"

        self.pool_info_address = "0xCF7e3DABBaD8F0F3fdf1AE8a13C4be3872d06d56"
        self.erc20_pool_abi_contract = "0x0E4a2276Ac259CF226eEC6536f2b447Fc26F2D8a"
        self.erc20_pool_factory_address = "0x0E4a2276Ac259CF226eEC6536f2b447Fc26F2D8a"
        self.erc20_pool_factory_start_block = 3916350

        self.erc721_pool_abi_contract = "0x07Eb44ca94cddA4016cECCe7FB9C7Ae73DBD4306"
        self.erc721_pool_factory_address = "0x07Eb44ca94cddA4016cECCe7FB9C7Ae73DBD4306"
        self.erc721_pool_factory_start_block = 3932342
        self.grant_fund_address = ""
        self.grant_fund_start_block = 0

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)

        # Celery task workaround
        # Since we need to access specific tasks sometimes (ethereum, base,...) we've
        # attached them to chain, since chain object is the base of almost everything
        from . import tasks

        self.celery_tasks = tasks
