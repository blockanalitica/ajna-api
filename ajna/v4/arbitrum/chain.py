import logging

from chain_harvester.networks.arbitrum.mainnet import ArbitrumMainnetChain
from django.conf import settings

from ajna.chain import AjnaChainMixin

from . import models

log = logging.getLogger(__name__)


MODEL_MAP = {
    "pool": models.V4ArbitrumPool,
    "token": models.V4ArbitrumToken,
    "pool_snapshot": models.V4ArbitrumPoolSnapshot,
    "bucket": models.V4ArbitrumBucket,
    "price_feed": models.V4ArbitrumPriceFeed,
    "pool_volume_snapshot": models.V4ArbitrumPoolVolumeSnapshot,
    "pool_event": models.V4ArbitrumPoolEvent,
    "current_wallet_position": models.V4ArbitrumCurrentWalletPoolPosition,
    "wallet_position": models.V4ArbitrumWalletPoolPosition,
    "wallet_bucket_state": models.V4ArbitrumWalletPoolBucketState,
    "bucket_state": models.V4ArbitrumPoolBucketState,
    "wallet": models.V4ArbitrumWallet,
    "notification": models.V4ArbitrumNotification,
    "auction": models.V4ArbitrumAuction,
    "auction_kick": models.V4ArbitrumAuctionKick,
    "auction_take": models.V4ArbitrumAuctionTake,
    "auction_bucket_take": models.V4ArbitrumAuctionBucketTake,
    "auction_settle": models.V4ArbitrumAuctionSettle,
    "auction_auction_settle": models.V4ArbitrumAuctionAuctionSettle,
    "auction_auction_nft_settle": models.V4ArbitrumAuctionAuctionNFTSettle,
    "reserve_auction": models.V4ArbitrumReserveAuction,
    "reserve_auction_kick": models.V4ArbitrumReserveAuctionKick,
    "reserve_auction_take": models.V4ArbitrumReserveAuctionTake,
    "activity_snapshot": models.V4ArbitrumActivitySnapshot,
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
        self.unique_key = "v4_arbitrum"

        self.pool_info_address = "0x8a7F5aFb7E3c3fD1f3Cc9D874b454b6De11EBbC9"
        self.erc20_pool_abi_contract = "0x6958750a77719D3432De3000436eF5d899b44278"
        self.erc20_pool_factory_address = "0xA3A1e968Bd6C578205E11256c8e6929f21742aAF"
        self.erc20_pool_factory_start_block = 171455195
        self.erc721_pool_abi_contract = "0x26f99c4ce8e2c94a8f2663b35dd7764851b53d27"
        self.erc721_pool_factory_address = "0x6ae3324612bEfD4AE460244c369f30Ab9CB8cAE2"
        self.erc721_pool_factory_start_block = 171455223
        self.grant_fund_address = ""
        self.grant_fund_start_block = 0

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)

        # Celery task workaround
        # Since we need to access specific tasks sometimes (ethereum, Base,...) we've
        # attached them to chain, since chain object is the base of almost everything
        from . import tasks

        self.celery_tasks = tasks
