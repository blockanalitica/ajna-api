from django.conf import settings

from ajna.chain import Blockchain

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


class Ethereum(Blockchain):
    def __init__(
        self,
        node=settings.ETHEREUM_NODE,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._node_address = node
        self.pool_info_address = "0x154FFf344f426F99E328bacf70f4Eb632210ecdc"
        for key, model in MODEL_MAP.items():
            setattr(self, key, model)

        # Celery task workaround
        # Since we need to access specific tasks sometimes (ethereum, goerli,...) we've
        # attached them to chain, since chain object is the base of almost everything
        from . import tasks

        self.celery_tasks = tasks
