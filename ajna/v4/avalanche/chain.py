import logging

from chain_harvester.networks.avalanche.mainnet import AvalancheMainnetChain
from django.conf import settings

from ajna.chain import AjnaChainMixin

from . import models

log = logging.getLogger(__name__)


MODEL_MAP = {
    "pool": models.V4AvalanchePool,
    "token": models.V4AvalancheToken,
    "pool_snapshot": models.V4AvalanchePoolSnapshot,
    "bucket": models.V4AvalancheBucket,
    "price_feed": models.V4AvalanchePriceFeed,
    "pool_volume_snapshot": models.V4AvalanchePoolVolumeSnapshot,
    "pool_event": models.V4AvalanchePoolEvent,
    "current_wallet_position": models.V4AvalancheCurrentWalletPoolPosition,
    "wallet_position": models.V4AvalancheWalletPoolPosition,
    "wallet_bucket_state": models.V4AvalancheWalletPoolBucketState,
    "bucket_state": models.V4AvalanchePoolBucketState,
    "wallet": models.V4AvalancheWallet,
    "notification": models.V4AvalancheNotification,
    "auction": models.V4AvalancheAuction,
    "auction_kick": models.V4AvalancheAuctionKick,
    "auction_take": models.V4AvalancheAuctionTake,
    "auction_bucket_take": models.V4AvalancheAuctionBucketTake,
    "auction_settle": models.V4AvalancheAuctionSettle,
    "auction_auction_settle": models.V4AvalancheAuctionAuctionSettle,
    "auction_auction_nft_settle": models.V4AvalancheAuctionAuctionNFTSettle,
    "reserve_auction": models.V4AvalancheReserveAuction,
    "reserve_auction_kick": models.V4AvalancheReserveAuctionKick,
    "reserve_auction_take": models.V4AvalancheReserveAuctionTake,
    "activity_snapshot": models.V4AvalancheActivitySnapshot,
}


class AvalancheModels:
    def __init__(self):
        super().__init__()

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)


class Avalanche(AjnaChainMixin, AvalancheMainnetChain):
    def __init__(self):
        super().__init__(
            rpc=settings.AVALANCHE_NODE
        )
        self.unique_key = "v4_avalanche"

        self.pool_info_address = "0x9e407019C07b50e8D7C2d0E2F796C4eCb0F485b3"
        self.erc20_pool_abi_contract = "0x275B348Bf5Cf7C973906ac3483392E497C5A0411"
        self.erc20_pool_factory_address = "0x2aA2A6e6B4b20f496A4Ed65566a6FD13b1b8A17A"
        self.erc20_pool_factory_start_block = 54484221
        self.erc721_pool_abi_contract = "0xfC41E5c6A108CCd70dcbbEF7BA508adCc51C612a"
        self.erc721_pool_factory_address = "0xB3d773147A086A23fB72dcc03828C66DcE5D6627"
        self.erc721_pool_factory_start_block = 54484221
        self.grant_fund_address = ""
        self.grant_fund_start_block = 0

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)

        # Celery task workaround
        # Since we need to access specific tasks sometimes (ethereum, Base,...) we've
        # attached them to chain, since chain object is the base of almost everything
        from . import tasks

        self.celery_tasks = tasks
