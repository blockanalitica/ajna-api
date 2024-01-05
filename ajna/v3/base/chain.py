import logging

from chain_harvester.networks.base.mainnet import BaseMainnetChain
from django.conf import settings

from ajna.chain import AjnaChainMixin

from . import models

log = logging.getLogger(__name__)


MODEL_MAP = {
    "pool": models.V3BasePool,
    "token": models.V3BaseToken,
    "pool_snapshot": models.V3BasePoolSnapshot,
    "bucket": models.V3BaseBucket,
    "price_feed": models.V3BasePriceFeed,
    "pool_volume_snapshot": models.V3BasePoolVolumeSnapshot,
    "pool_event": models.V3BasePoolEvent,
    "current_wallet_position": models.V3BaseCurrentWalletPoolPosition,
    "wallet_position": models.V3BaseWalletPoolPosition,
    "wallet_bucket_state": models.V3BaseWalletPoolBucketState,
    "bucket_state": models.V3BasePoolBucketState,
    "wallet": models.V3BaseWallet,
    "notification": models.V3BaseNotification,
    "auction": models.V3BaseAuction,
    "auction_kick": models.V3BaseAuctionKick,
    "auction_take": models.V3BaseAuctionTake,
    "auction_bucket_take": models.V3BaseAuctionBucketTake,
    "auction_settle": models.V3BaseAuctionSettle,
    "auction_auction_settle": models.V3BaseAuctionAuctionSettle,
    "auction_auction_nft_settle": models.V3BaseAuctionAuctionNFTSettle,
    "reserve_auction": models.V3BaseReserveAuction,
    "reserve_auction_kick": models.V3BaseReserveAuctionKick,
    "reserve_auction_take": models.V3BaseReserveAuctionTake,
    "grant_distribution_period": models.V3BaseGrantDistributionPeriod,
    "grant_proposal": models.V3BaseGrantProposal,
    "grant_event": models.V3BaseGrantEvent,
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
        self.unique_key = "v3_base"

        self.pool_info_address = "0x1358e3be37C191Eb5B842F673fcB5C79Cc4F6644"
        self.erc20_pool_abi_contract = ""
        self.erc20_pool_factory_address = "0x154FFf344f426F99E328bacf70f4Eb632210ecdc"
        self.erc20_pool_factory_start_block = 8797468
        self.erc721_pool_abi_contract = ""
        self.erc721_pool_factory_address = "0xd8B6729E20d141a03eC4BcAC17F1441CD85975C3"
        self.erc721_pool_factory_start_block = 8797472
        self.grant_fund_address = ""
        self.grant_fund_start_block = 0

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)

        # Celery task workaround
        # Since we need to access specific tasks sometimes (ethereum, Base,...) we've
        # attached them to chain, since chain object is the base of almost everything
        from . import tasks

        self.celery_tasks = tasks
