import logging

from chain_harvester.networks.gnosis.mainnet import GnosisMainnetChain
from django.conf import settings

from ajna.chain import AjnaChainMixin

from . import models

log = logging.getLogger(__name__)


MODEL_MAP = {
    "pool": models.V4GnosisPool,
    "token": models.V4GnosisToken,
    "pool_snapshot": models.V4GnosisPoolSnapshot,
    "bucket": models.V4GnosisBucket,
    "price_feed": models.V4GnosisPriceFeed,
    "pool_volume_snapshot": models.V4GnosisPoolVolumeSnapshot,
    "pool_event": models.V4GnosisPoolEvent,
    "current_wallet_position": models.V4GnosisCurrentWalletPoolPosition,
    "wallet_position": models.V4GnosisWalletPoolPosition,
    "wallet_bucket_state": models.V4GnosisWalletPoolBucketState,
    "bucket_state": models.V4GnosisPoolBucketState,
    "wallet": models.V4GnosisWallet,
    "notification": models.V4GnosisNotification,
    "auction": models.V4GnosisAuction,
    "auction_kick": models.V4GnosisAuctionKick,
    "auction_take": models.V4GnosisAuctionTake,
    "auction_bucket_take": models.V4GnosisAuctionBucketTake,
    "auction_settle": models.V4GnosisAuctionSettle,
    "auction_auction_settle": models.V4GnosisAuctionAuctionSettle,
    "auction_auction_nft_settle": models.V4GnosisAuctionAuctionNFTSettle,
    "reserve_auction": models.V4GnosisReserveAuction,
    "reserve_auction_kick": models.V4GnosisReserveAuctionKick,
    "reserve_auction_take": models.V4GnosisReserveAuctionTake,
}


class GnosisModels:
    def __init__(self):
        super().__init__()

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)


class Gnosis(AjnaChainMixin, GnosisMainnetChain):
    def __init__(self):
        super().__init__(
            rpc=settings.GNOSIS_NODE,
            api_key=settings.GNOSISSCAN_API_KEY,
            step=10000,
            abis_path="abis/gnosis/",
        )
        self.unique_key = "v4_gnosis"

        self.pool_info_address = "0x2baB4c287cF33a6eC373CFE152FdbA299B653F7D"
        self.erc20_pool_abi_contract = "0x6CE07299999Aed9838c0d7b2a61802D0eBb47358"
        self.erc20_pool_factory_address = "0x87578E357358163FCAb1711c62AcDB5BBFa1C9ef"
        self.erc20_pool_factory_start_block = 32086484
        self.erc721_pool_abi_contract = "0xdEf017D6E23E4a4292D299035D0f887769adA392"
        self.erc721_pool_factory_address = "0xc7Fc13Fa7B697fBE3bdC56D5b9A6586A83254126"
        self.erc721_pool_factory_start_block = 32086512
        self.grant_fund_address = ""
        self.grant_fund_start_block = 0

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)

        # Celery task workaround
        # Since we need to access specific tasks sometimes (ethereum, Base,...) we've
        # attached them to chain, since chain object is the base of almost everything
        from . import tasks

        self.celery_tasks = tasks
