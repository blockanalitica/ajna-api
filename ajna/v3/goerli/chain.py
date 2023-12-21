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
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)


class Goerli(AjnaChainMixin, EthereumGoerliChain):
    def __init__(self, *args, **kwargs):
        super().__init__(
            rpc=settings.GOERLI_NODE,
            api_key=settings.ETHERSCAN_API_KEY,
            step=50000,
            *args,
            **kwargs,
        )
        self.unique_key = "v3_goerli"

        self.pool_info_address = "0x3c5cf15122903C7CabcAA49FcfC090D3A311C038"
        self.erc20_pool_abi_contract = ""
        self.erc20_pool_factory_address = "0xA2d6694F24c84e428B97bF9fCD8E3e3dba3023D0"
        self.erc20_pool_factory_start_block = 10243942
        self.erc721_pool_abi_contract = "0x9B9E6e18FeAE6e360927817d06bDA5a52Ad0E3Ec"
        self.erc721_pool_factory_address = "0x0CC0Ba1bC6f45513422D6BF301Bd1Cb8c78B5861"
        self.erc721_pool_factory_start_block = 10243943
        self.grant_fund_address = ""
        self.grant_fund_start_block = 0

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)

        # Celery task workaround
        # Since we need to access specific tasks sometimes (ethereum, goerli,...) we've
        # attached them to chain, since chain object is the base of almost everything
        from . import tasks

        self.celery_tasks = tasks
