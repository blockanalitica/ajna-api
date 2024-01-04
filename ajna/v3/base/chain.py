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
            api_key=settings.ETHERSCAN_API_KEY,
            step=50000,
        )
        self.unique_key = "v3_base"

        self.pool_info_address = "0xC086acc9Bf89D8a0E2209e2870fC020D8f3323a8"
        self.erc20_pool_abi_contract = ""
        self.erc20_pool_factory_address = "0xdc01502485c02496a929c12762cE99Fd755c6a25"
        self.erc20_pool_factory_start_block = 8156311
        self.erc721_pool_abi_contract = ""
        self.erc721_pool_factory_address = "0x513cc6E8De2FC3c7532d867fc6c287ABb56df230"
        self.erc721_pool_factory_start_block = 8156315
        self.grant_fund_address = ""
        self.grant_fund_start_block = 0

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)

        # Celery task workaround
        # Since we need to access specific tasks sometimes (ethereum, Base,...) we've
        # attached them to chain, since chain object is the base of almost everything
        from . import tasks

        self.celery_tasks = tasks
