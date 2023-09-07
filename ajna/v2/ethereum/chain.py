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
    "remove_collateral": models.V2EthereumRemoveCollateral,
    "add_collateral": models.V2EthereumAddCollateral,
    "add_quote_token": models.V2EthereumAddQuoteToken,
    "remove_quote_token": models.V2EthereumRemoveQuoteToken,
    "move_quote_token": models.V2EthereumMoveQuoteToken,
    "draw_debt": models.V2EthereumDrawDebt,
    "repay_debt": models.V2EthereumRepayDebt,
    "liqudation_auction": models.V2EthereumLiquidationAuction,
    "pool_volume_snapshot": models.V2EthereumPoolVolumeSnapshot,
    "grant_proposal": models.V2EthereumGrantProposal,
    "pool_event": models.V2EthereumPoolEvent,
    "current_wallet_position": models.V2EthereumCurrentWalletPoolPosition,
    "wallet_position": models.V2EthereumWalletPoolPosition,
    "wallet_bucket_state": models.V2EthereumWalletPoolBucketState,
    "bucket_state": models.V2EthereumPoolBucketState,
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

        # TODO: wrong addresses (these are from v1)
        self.pool_info_address = "0x154FFf344f426F99E328bacf70f4Eb632210ecdc"
        self.erc20_pool_abi_contract = "0x05bB4F6362B02F17C1A3F2B047A8b23368269A21"
        self.erc20_pool_factory_address = "0xe6F4d9711121e5304b30aC2Aae57E3b085ad3c4d"
        self.erc20_pool_factory_start_block = 17622995

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)

        # Celery task workaround
        # Since we need to access specific tasks sometimes (ethereum, goerli,...) we've
        # attached them to chain, since chain object is the base of almost everything
        from . import tasks

        self.celery_tasks = tasks
