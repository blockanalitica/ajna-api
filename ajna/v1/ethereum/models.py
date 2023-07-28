from ...models import base


class V1EthereumPool(base.Pool):
    pass


class V1EthereumPoolSnapshot(base.PoolSnapshot):
    pass


class V1EthereumToken(base.Token):
    pass


class V1EthereumBucket(base.Bucket):
    pass


class V1EthereumPriceFeed(base.PriceFeed):
    pass


class V1EthereumRemoveCollateral(base.RemoveCollateral):
    pass


class V1EthereumAddCollateral(base.AddCollateral):
    pass


class V1EthereumAddQuoteToken(base.AddQuoteToken):
    pass


class V1EthereumRemoveQuoteToken(base.RemoveQuoteToken):
    pass


class V1EthereumMoveQuoteToken(base.MoveQuoteToken):
    pass


class V1EthereumDrawDebt(base.DrawDebt):
    pass


class V1EthereumRepayDebt(base.RepayDebt):
    pass


class V1EthereumLiquidationAuction(base.LiquidationAuction):
    pass


class V1EthereumPoolVolumeSnapshot(base.PoolVolumeSnapshot):
    pass
