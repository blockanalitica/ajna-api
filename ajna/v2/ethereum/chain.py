from chain_harvester.networks.ethereum.mainnet import EthereumMainnetChain
from django.conf import settings

from ajna.chain import AjnaChainMixin

from . import models

MODEL_MAP = {
    "pool": models.V2EthereumPool,
    "token": models.V2EthereumToken,
    "pool_snapshot": models.V2EthereumPoolSnapshot,
    "bucket": models.V2EthereumBucket,
    "price_feed": models.V2EthereumPriceFeed,
    "pool_volume_snapshot": models.V2EthereumPoolVolumeSnapshot,
    "pool_event": models.V2EthereumPoolEvent,
    "current_wallet_position": models.V2EthereumCurrentWalletPoolPosition,
    "wallet_position": models.V2EthereumWalletPoolPosition,
    "wallet_bucket_state": models.V2EthereumWalletPoolBucketState,
    "bucket_state": models.V2EthereumPoolBucketState,
    "wallet": models.V2EthereumWallet,
    "notification": models.V2EthereumNotification,
    "auction": models.V2EthereumAuction,
    "auction_kick": models.V2EthereumAuctionKick,
    "auction_take": models.V2EthereumAuctionTake,
    "auction_bucket_take": models.V2EthereumAuctionBucketTake,
    "auction_settle": models.V2EthereumAuctionSettle,
    "auction_auction_settle": models.V2EthereumAuctionAuctionSettle,
    "reserve_auction": models.V2EthereumReserveAuction,
    "reserve_auction_kick": models.V2EthereumReserveAuctionKick,
    "reserve_auction_take": models.V2EthereumReserveAuctionTake,
    "grant_distribution_period": models.V2EthereumGrantDistributionPeriod,
    "grant_proposal": models.V2EthereumGrantProposal,
    "grant_event": models.V2EthereumGrantEvent,
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
        self.unique_key = "v2_ethereum"

        # TODO: wrong addresses (these are from v1)
        self.pool_info_address = "0x154FFf344f426F99E328bacf70f4Eb632210ecdc"
        self.erc20_pool_abi_contract = "0x05bB4F6362B02F17C1A3F2B047A8b23368269A21"
        self.erc20_pool_factory_address = "0xe6F4d9711121e5304b30aC2Aae57E3b085ad3c4d"
        self.erc20_pool_factory_start_block = 17622995
        self.erc721_pool_abi_contract = "0xe19b31c00c01ab38ea279e93ac66ca773d314c91"
        self.erc721_pool_factory_address = "0xb8DA113516bfb986B7b8738a76C136D1c16c5609"
        self.erc721_pool_factory_start_block = 17622995
        self.grant_fund_address = ""  # TODO
        self.grant_fund_start_block = 0  # TODO

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)

        # Celery task workaround
        # Since we need to access specific tasks sometimes (ethereum, goerli,...) we've
        # attached them to chain, since chain object is the base of almost everything
        from . import tasks

        self.celery_tasks = tasks
