import logging

from chain_harvester.networks.arbitrum.mainnet import ArbitrumMainnetChain
from django.conf import settings

from ajna.chain import AjnaChainMixin

from . import models

log = logging.getLogger(__name__)


MODEL_MAP = {
    "pool": models.V3ArbitrumPool,
    "token": models.V3ArbitrumToken,
    "pool_snapshot": models.V3ArbitrumPoolSnapshot,
    "bucket": models.V3ArbitrumBucket,
    "price_feed": models.V3ArbitrumPriceFeed,
    "pool_volume_snapshot": models.V3ArbitrumPoolVolumeSnapshot,
    "pool_event": models.V3ArbitrumPoolEvent,
    "current_wallet_position": models.V3ArbitrumCurrentWalletPoolPosition,
    "wallet_position": models.V3ArbitrumWalletPoolPosition,
    "wallet_bucket_state": models.V3ArbitrumWalletPoolBucketState,
    "bucket_state": models.V3ArbitrumPoolBucketState,
    "wallet": models.V3ArbitrumWallet,
    "notification": models.V3ArbitrumNotification,
    "auction": models.V3ArbitrumAuction,
    "auction_kick": models.V3ArbitrumAuctionKick,
    "auction_take": models.V3ArbitrumAuctionTake,
    "auction_bucket_take": models.V3ArbitrumAuctionBucketTake,
    "auction_settle": models.V3ArbitrumAuctionSettle,
    "auction_auction_settle": models.V3ArbitrumAuctionAuctionSettle,
    "auction_auction_nft_settle": models.V3ArbitrumAuctionAuctionNFTSettle,
    "reserve_auction": models.V3ArbitrumReserveAuction,
    "reserve_auction_kick": models.V3ArbitrumReserveAuctionKick,
    "reserve_auction_take": models.V3ArbitrumReserveAuctionTake,
    "grant_distribution_period": models.V3ArbitrumGrantDistributionPeriod,
    "grant_proposal": models.V3ArbitrumGrantProposal,
    "grant_event": models.V3ArbitrumGrantEvent,
}


class ArbitrumModels:
    def __init__(self):
        super().__init__()

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)


class Arbitrum(AjnaChainMixin, ArbitrumMainnetChain):
    def __init__(self):
        super().__init__(
            rpc=settings.ARBITRUM_NODE,
            api_key=settings.ARBISCAN_API_KEY,
            step=50000,
        )
        self.unique_key = "v3_arbitrum"

        self.pool_info_address = "0x08432Bb9A4D302450fFAaFD647A0A121D3a143cC"
        self.erc20_pool_abi_contract = ""
        self.erc20_pool_factory_address = "0x595c823EdAA612972d77aCf324C11F6284B9f5F6"
        self.erc20_pool_factory_start_block = 167209839
        self.erc721_pool_abi_contract = ""
        self.erc721_pool_factory_address = "0xA9Ada58DD3c820b30D3bf5B490226F2ef92107bA"
        self.erc721_pool_factory_start_block = 167209865
        self.grant_fund_address = ""
        self.grant_fund_start_block = 0

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)

        # Celery task workaround
        # Since we need to access specific tasks sometimes (ethereum, Base,...) we've
        # attached them to chain, since chain object is the base of almost everything
        from . import tasks

        self.celery_tasks = tasks
