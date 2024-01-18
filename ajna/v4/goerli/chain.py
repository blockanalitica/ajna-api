"""
NOTE: v4 of goerli is the same as v3!
They've redeployed only L2s for the v4 version.
"""

from chain_harvester.networks.ethereum.goerli import EthereumGoerliChain
from django.conf import settings

from ajna.chain import AjnaChainMixin

from . import models

MODEL_MAP = {
    "pool": models.V3GoerliPool,
    "token": models.V3GoerliToken,
    "pool_snapshot": models.V3GoerliPoolSnapshot,
    "bucket": models.V3GoerliBucket,
    "price_feed": models.V3GoerliPriceFeed,
    "pool_volume_snapshot": models.V3GoerliPoolVolumeSnapshot,
    "pool_event": models.V3GoerliPoolEvent,
    "current_wallet_position": models.V3GoerliCurrentWalletPoolPosition,
    "wallet_position": models.V3GoerliWalletPoolPosition,
    "wallet_bucket_state": models.V3GoerliWalletPoolBucketState,
    "bucket_state": models.V3GoerliPoolBucketState,
    "wallet": models.V3GoerliWallet,
    "notification": models.V3GoerliNotification,
    "auction": models.V3GoerliAuction,
    "auction_kick": models.V3GoerliAuctionKick,
    "auction_take": models.V3GoerliAuctionTake,
    "auction_bucket_take": models.V3GoerliAuctionBucketTake,
    "auction_settle": models.V3GoerliAuctionSettle,
    "auction_auction_settle": models.V3GoerliAuctionAuctionSettle,
    "auction_auction_nft_settle": models.V3GoerliAuctionAuctionNFTSettle,
    "reserve_auction": models.V3GoerliReserveAuction,
    "reserve_auction_kick": models.V3GoerliReserveAuctionKick,
    "reserve_auction_take": models.V3GoerliReserveAuctionTake,
    "grant_distribution_period": models.V3GoerliGrantDistributionPeriod,
    "grant_proposal": models.V3GoerliGrantProposal,
    "grant_event": models.V3GoerliGrantEvent,
}


class GoerliModels:
    def __init__(
        self,
    ):
        super().__init__()

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)


class Goerli(AjnaChainMixin, EthereumGoerliChain):
    def __init__(self):
        super().__init__(
            rpc=settings.GOERLI_NODE,
            api_key=settings.ETHERSCAN_API_KEY,
            step=50000,
        )
        self.unique_key = "v3_goerli"

        self.pool_info_address = "0xdE8D83e069F552fbf3EE5bF04E8C4fa53a097ee5"
        self.erc20_pool_abi_contract = "0x9e5cA171E98Cb8F7b77EFc80858fF2079f80e114"
        self.erc20_pool_factory_address = "0xDB61f8aD0B3ed0c5522b8FE71b80023fe9188e9e"
        self.erc20_pool_factory_start_block = 10321610
        self.erc721_pool_abi_contract = "0x3CC3B4AadbdBDCDda7e1DC12427587Af0F275a23"
        self.erc721_pool_factory_address = "0x8FA83D458CDbB2FCeA66d9bc31FDa80511e0AA56"
        self.erc721_pool_factory_start_block = 10321611
        self.grant_fund_address = "0x1b8cDBDcffD4fBdC66dC8540227F007901a196C5"
        self.grant_fund_start_block = 10327592

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)

        # Celery task workaround
        # Since we need to access specific tasks sometimes (ethereum, goerli,...) we've
        # attached them to chain, since chain object is the base of almost everything
        from . import tasks

        self.celery_tasks = tasks
