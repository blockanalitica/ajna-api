import logging

from chain_harvester.networks.rari.mainnet import RariMainnetChain
from django.conf import settings

from ajna.chain import AjnaChainMixin

from . import models

log = logging.getLogger(__name__)


MODEL_MAP = {
    "pool": models.V4RariPool,
    "token": models.V4RariToken,
    "pool_snapshot": models.V4RariPoolSnapshot,
    "bucket": models.V4RariBucket,
    "price_feed": models.V4RariPriceFeed,
    "pool_volume_snapshot": models.V4RariPoolVolumeSnapshot,
    "pool_event": models.V4RariPoolEvent,
    "current_wallet_position": models.V4RariCurrentWalletPoolPosition,
    "wallet_position": models.V4RariWalletPoolPosition,
    "wallet_bucket_state": models.V4RariWalletPoolBucketState,
    "bucket_state": models.V4RariPoolBucketState,
    "wallet": models.V4RariWallet,
    "notification": models.V4RariNotification,
    "auction": models.V4RariAuction,
    "auction_kick": models.V4RariAuctionKick,
    "auction_take": models.V4RariAuctionTake,
    "auction_bucket_take": models.V4RariAuctionBucketTake,
    "auction_settle": models.V4RariAuctionSettle,
    "auction_auction_settle": models.V4RariAuctionAuctionSettle,
    "auction_auction_nft_settle": models.V4RariAuctionAuctionNFTSettle,
    "reserve_auction": models.V4RariReserveAuction,
    "reserve_auction_kick": models.V4RariReserveAuctionKick,
    "reserve_auction_take": models.V4RariReserveAuctionTake,
    "activity_snapshot": models.V4RariActivitySnapshot,
}


class RariModels:
    def __init__(self):
        super().__init__()

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)


class Rari(AjnaChainMixin, RariMainnetChain):
    def __init__(self):
        super().__init__(
            rpc=settings.RARI_NODE,
            api_key="n/a",
            step=10000,
        )
        self.unique_key = "v4_rari"

        self.pool_info_address = "0xe85958CD5d59755470F6217aE9ee2Aa88eD02eE5"
        self.erc20_pool_abi_contract = "0xf62f3A8d44973c8A16c49621C5d79CF58E5dc77B"
        self.erc20_pool_factory_address = "0x10cE36851B0aAf4b5FCAdc93f176aC441D4819c9"
        self.erc20_pool_factory_start_block = 399383
        self.erc721_pool_abi_contract = "0xC91C52D30347b8Ef7C75F0a93Fdd70E19e05b5e8"
        self.erc721_pool_factory_address = "0x9A846d9871012f948c11357c19088007Ee6845BC"
        self.erc721_pool_factory_start_block = 399410
        self.grant_fund_address = ""
        self.grant_fund_start_block = 0

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)

        # Celery task workaround
        # Since we need to access specific tasks sometimes (ethereum, base,...) we've
        # attached them to chain, since chain object is the base of almost everything
        from . import tasks

        self.celery_tasks = tasks
