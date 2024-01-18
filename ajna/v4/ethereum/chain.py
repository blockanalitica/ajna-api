"""
NOTE: v4 of ethereum is the same as v3!
They've redeployed only L2s for the v4 version.
"""

from chain_harvester.networks.ethereum.mainnet import EthereumMainnetChain
from django.conf import settings

from ajna.chain import AjnaChainMixin

from . import models

MODEL_MAP = {
    "pool": models.V3EthereumPool,
    "token": models.V3EthereumToken,
    "pool_snapshot": models.V3EthereumPoolSnapshot,
    "bucket": models.V3EthereumBucket,
    "price_feed": models.V3EthereumPriceFeed,
    "pool_volume_snapshot": models.V3EthereumPoolVolumeSnapshot,
    "pool_event": models.V3EthereumPoolEvent,
    "current_wallet_position": models.V3EthereumCurrentWalletPoolPosition,
    "wallet_position": models.V3EthereumWalletPoolPosition,
    "wallet_bucket_state": models.V3EthereumWalletPoolBucketState,
    "bucket_state": models.V3EthereumPoolBucketState,
    "wallet": models.V3EthereumWallet,
    "notification": models.V3EthereumNotification,
    "auction": models.V3EthereumAuction,
    "auction_kick": models.V3EthereumAuctionKick,
    "auction_take": models.V3EthereumAuctionTake,
    "auction_bucket_take": models.V3EthereumAuctionBucketTake,
    "auction_settle": models.V3EthereumAuctionSettle,
    "auction_auction_settle": models.V3EthereumAuctionAuctionSettle,
    "auction_auction_nft_settle": models.V3EthereumAuctionAuctionNFTSettle,
    "reserve_auction": models.V3EthereumReserveAuction,
    "reserve_auction_kick": models.V3EthereumReserveAuctionKick,
    "reserve_auction_take": models.V3EthereumReserveAuctionTake,
    "grant_distribution_period": models.V3EthereumGrantDistributionPeriod,
    "grant_proposal": models.V3EthereumGrantProposal,
    "grant_event": models.V3EthereumGrantEvent,
}


class EthereumModels:
    def __init__(self):
        super().__init__()

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)


class Ethereum(AjnaChainMixin, EthereumMainnetChain):
    def __init__(self):
        super().__init__(
            rpc=settings.ETHEREUM_NODE,
            api_key=settings.ETHERSCAN_API_KEY,
            step=50000,
        )
        self.unique_key = "v3_ethereum"

        self.pool_info_address = "0x30c5eF2997d6a882DE52c4ec01B6D0a5e5B4fAAE"
        self.erc20_pool_abi_contract = "0x4B3B9A972a884e37FD675ee57F6998da0BE47e26"
        self.erc20_pool_factory_address = "0x6146DD43C5622bB6D12A5240ab9CF4de14eDC625"
        self.erc20_pool_factory_start_block = 18938158
        self.erc721_pool_abi_contract = "0xb0f4D8E3b28B9D2d27523c9050beD1c44bcF9CAF"
        self.erc721_pool_factory_address = "0x27461199d3b7381De66a85D685828E967E35AF4c"
        self.erc721_pool_factory_start_block = 18938159
        self.grant_fund_address = "0x74d5b005ca64a5C9EE3611Bdc6F6C02D93C84b2f"
        self.grant_fund_start_block = 18964103

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)

        # Celery task workaround
        # Since we need to access specific tasks sometimes (ethereum, goerli,...) we've
        # attached them to chain, since chain object is the base of almost everything
        from . import tasks

        self.celery_tasks = tasks
