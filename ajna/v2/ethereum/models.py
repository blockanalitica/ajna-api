from ...models import base


class V2EthereumPool(base.Pool):
    pass


class V2EthereumPoolSnapshot(base.PoolSnapshot):
    pass


class V2EthereumToken(base.Token):
    pass


class V2EthereumBucket(base.Bucket):
    pass


class V2EthereumPriceFeed(base.PriceFeed):
    pass


class V2EthereumRemoveCollateral(base.RemoveCollateral):
    pass


class V2EthereumAddCollateral(base.AddCollateral):
    pass


class V2EthereumAddQuoteToken(base.AddQuoteToken):
    pass


class V2EthereumRemoveQuoteToken(base.RemoveQuoteToken):
    pass


class V2EthereumMoveQuoteToken(base.MoveQuoteToken):
    pass


class V2EthereumDrawDebt(base.DrawDebt):
    pass


class V2EthereumRepayDebt(base.RepayDebt):
    pass


class V2EthereumLiquidationAuction(base.LiquidationAuction):
    pass


class V2EthereumPoolVolumeSnapshot(base.PoolVolumeSnapshot):
    pass


class V2EthereumGrantProposal(base.GrantProposal):
    pass


class V2EthereumPoolEvent(base.PoolEvent):
    pass
