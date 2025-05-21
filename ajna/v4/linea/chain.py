import logging

from chain_harvester.networks.linea.mainnet import LineaMainnetChain
from django.conf import settings

from ajna.chain import AjnaChainMixin

from . import models

log = logging.getLogger(__name__)


MODEL_MAP = {
    "pool": models.V4LineaPool,
    "token": models.V4LineaToken,
    "pool_snapshot": models.V4LineaPoolSnapshot,
    "bucket": models.V4LineaBucket,
    "price_feed": models.V4LineaPriceFeed,
    "pool_volume_snapshot": models.V4LineaPoolVolumeSnapshot,
    "pool_event": models.V4LineaPoolEvent,
    "current_wallet_position": models.V4LineaCurrentWalletPoolPosition,
    "wallet_position": models.V4LineaWalletPoolPosition,
    "wallet_bucket_state": models.V4LineaWalletPoolBucketState,
    "bucket_state": models.V4LineaPoolBucketState,
    "wallet": models.V4LineaWallet,
    "notification": models.V4LineaNotification,
    "auction": models.V4LineaAuction,
    "auction_kick": models.V4LineaAuctionKick,
    "auction_take": models.V4LineaAuctionTake,
    "auction_bucket_take": models.V4LineaAuctionBucketTake,
    "auction_settle": models.V4LineaAuctionSettle,
    "auction_auction_settle": models.V4LineaAuctionAuctionSettle,
    "auction_auction_nft_settle": models.V4LineaAuctionAuctionNFTSettle,
    "reserve_auction": models.V4LineaReserveAuction,
    "reserve_auction_kick": models.V4LineaReserveAuctionKick,
    "reserve_auction_take": models.V4LineaReserveAuctionTake,
    "activity_snapshot": models.V4LineaActivitySnapshot,
}


class LineaModels:
    def __init__(self):
        super().__init__()

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)


class Linea(AjnaChainMixin, LineaMainnetChain):
    def __init__(self):
        super().__init__(
            rpc=settings.LINEA_NODE,
            etherscan_api_key=settings.ETHERSCAN_API_KEY,
            step=1_000_000,
        )
        self.unique_key = "v4_linea"

        self.pool_info_address = "0x3AFcEcB6A943746eccd72eb6801E534f8887eEA1"
        self.erc20_pool_abi_contract = "0xbddf1fc245a79bbf3eb7025fa3b114d061c23c6c"
        self.erc20_pool_factory_address = "0xd72A448C3BC8f47EAfFc2C88Cf9aC9423Bfb5067"
        self.erc20_pool_factory_start_block = 5770219
        self.erc721_pool_abi_contract = "0x0259d67f1c26ee2d48b305c5651d8a12aad7033e"
        self.erc721_pool_factory_address = "0x0c1Fa8D707dFb57551efa21C16255BEAb13F5bCD"
        self.erc721_pool_factory_start_block = 5770219
        self.grant_fund_address = ""
        self.grant_fund_start_block = 0

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)

        # Celery task workaround
        # Since we need to access specific tasks sometimes (ethereum, Base,...) we've
        # attached them to chain, since chain object is the base of almost everything
        from . import tasks

        self.celery_tasks = tasks
