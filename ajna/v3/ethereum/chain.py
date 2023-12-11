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
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)


class Ethereum(AjnaChainMixin, EthereumMainnetChain):
    def __init__(self, *args, **kwargs):
        super().__init__(
            rpc=settings.ETHEREUM_NODE,
            api_key=settings.ETHERSCAN_API_KEY,
            step=50000,
            *args,
            **kwargs,
        )
        self.unique_key = "v3_ethereum"

        self.pool_info_address = "0xd51789b0B9b6be8A89778e3C93cC365511bf382c"
        self.erc20_pool_abi_contract = "0x91d3b65B54C55c1337C01d6C8aa36fc0D3Bcf8e9"
        self.erc20_pool_factory_address = "0x33960C912b67Fe1Abf4738e2b754d299d99cF2F1"
        self.erc20_pool_factory_start_block = 18727005
        self.erc721_pool_abi_contract = ""
        self.erc721_pool_factory_address = "0x82078B0E5bA5Fe7Cd2894B66902144F346772A5C"
        self.erc721_pool_factory_start_block = 18727006
        self.grant_fund_address = ""
        self.grant_fund_start_block = 0

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)

        # Celery task workaround
        # Since we need to access specific tasks sometimes (ethereum, goerli,...) we've
        # attached them to chain, since chain object is the base of almost everything
        from . import tasks

        self.celery_tasks = tasks
