from chain_harvester.networks.ethereum.goerli import EthereumGoerliChain
from django.conf import settings

from ajna.chain import AjnaChainMixin

from . import models

MODEL_MAP = {
    "pool": models.V1GoerliPool,
    "token": models.V1GoerliToken,
    "pool_snapshot": models.V1GoerliPoolSnapshot,
    "bucket": models.V1GoerliBucket,
    "price_feed": models.V1GoerliPriceFeed,
    "remove_collateral": models.V1GoerliRemoveCollateral,
    "add_collateral": models.V1GoerliAddCollateral,
    "add_quote_token": models.V1GoerliAddQuoteToken,
    "remove_quote_token": models.V1GoerliRemoveQuoteToken,
    "move_quote_token": models.V1GoerliMoveQuoteToken,
    "draw_debt": models.V1GoerliDrawDebt,
    "repay_debt": models.V1GoerliRepayDebt,
    "liqudation_auction": models.V1GoerliLiquidationAuction,
    "pool_volume_snapshot": models.V1GoerliPoolVolumeSnapshot,
    "grant_proposal": models.V1GoerliGrantProposal,
    "pool_event": models.V1GoerliPoolEvent,
    "current_wallet_position": models.V1GoerliCurrentWalletPoolPosition,
    "wallet_position": models.V1GoerliWalletPoolPosition,
    "wallet_bucket_state": models.V1GoerliWalletPoolBucketState,
    "bucket_state": models.V1GoerliPoolBucketState,
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
        self.pool_info_address = "0xBB61407715cDf92b2784E9d2F1675c4B8505cBd8"
        self.erc20_pool_abi_contract = "0x6e173d30ccd286577ed7eeedc0cd4a6caeb7a669"
        for key, model in MODEL_MAP.items():
            setattr(self, key, model)

        # Celery task workaround
        # Since we need to access specific tasks sometimes (ethereum, goerli,...) we've
        # attached them to chain, since chain object is the base of almost everything
        from . import tasks

        self.celery_tasks = tasks
