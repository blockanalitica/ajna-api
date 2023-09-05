from ...models import base


class V2GoerliPool(base.Pool):
    pass


class V2GoerliPoolSnapshot(base.PoolSnapshot):
    pass


class V2GoerliToken(base.Token):
    pass


class V2GoerliBucket(base.Bucket):
    pass


class V2GoerliPriceFeed(base.PriceFeed):
    pass


class V2GoerliRemoveCollateral(base.RemoveCollateral):
    pass


class V2GoerliAddCollateral(base.AddCollateral):
    pass


class V2GoerliAddQuoteToken(base.AddQuoteToken):
    pass


class V2GoerliRemoveQuoteToken(base.RemoveQuoteToken):
    pass


class V2GoerliMoveQuoteToken(base.MoveQuoteToken):
    pass


class V2GoerliDrawDebt(base.DrawDebt):
    pass


class V2GoerliRepayDebt(base.RepayDebt):
    pass


class V2GoerliLiquidationAuction(base.LiquidationAuction):
    pass


class V2GoerliPoolVolumeSnapshot(base.PoolVolumeSnapshot):
    pass


class V2GoerliGrantProposal(base.GrantProposal):
    pass


class V2GoerliPoolEvent(base.PoolEvent):
    pass
