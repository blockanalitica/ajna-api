from chain_harvester.networks.ethereum.mainnet import EthereumMainnetChain
from django.conf import settings

from ajna.chain import AjnaChainMixin

from . import models

MODEL_MAP = {
    "pool": models.V1EthereumPool,
    "token": models.V1EthereumToken,
    "pool_snapshot": models.V1EthereumPoolSnapshot,
    "bucket": models.V1EthereumBucket,
    "price_feed": models.V1EthereumPriceFeed,
    "remove_collateral": models.V1EthereumRemoveCollateral,
    "add_collateral": models.V1EthereumAddCollateral,
    "add_quote_token": models.V1EthereumAddQuoteToken,
    "remove_quote_token": models.V1EthereumRemoveQuoteToken,
    "move_quote_token": models.V1EthereumMoveQuoteToken,
    "draw_debt": models.V1EthereumDrawDebt,
    "repay_debt": models.V1EthereumRepayDebt,
    "liqudation_auction": models.V1EthereumLiquidationAuction,
    "pool_volume_snapshot": models.V1EthereumPoolVolumeSnapshot,
    "grant_proposal": models.V1EthereumGrantProposal,
    "pool_event": models.V1EthereumPoolEvent,
    "current_wallet_position": models.V1EthereumCurrentWalletPoolPosition,
    "wallet_position": models.V1EthereumWalletPoolPosition,
    "wallet_bucket_state": models.V1EthereumWalletPoolBucketState,
    "bucket_state": models.V1EthereumPoolBucketState,
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
            step=50000,
            api_key=settings.ETHERSCAN_API_KEY,
            *args,
            **kwargs,
        )
        self.pool_info_address = "0x154FFf344f426F99E328bacf70f4Eb632210ecdc"
        self.erc20_pool_default_contract = "0x05bB4F6362B02F17C1A3F2B047A8b23368269A21"

        for key, model in MODEL_MAP.items():
            setattr(self, key, model)

        # Celery task workaround
        # Since we need to access specific tasks sometimes (ethereum, goerli,...) we've
        # attached them to chain, since chain object is the base of almost everything
        from . import tasks

        self.celery_tasks = tasks
