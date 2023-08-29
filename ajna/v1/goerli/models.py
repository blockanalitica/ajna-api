from ...models import base


class V1GoerliPool(base.Pool):
    pass


class V1GoerliPoolSnapshot(base.PoolSnapshot):
    pass


class V1GoerliToken(base.Token):
    pass


class V1GoerliBucket(base.Bucket):
    pass


class V1GoerliPriceFeed(base.PriceFeed):
    pass


class V1GoerliRemoveCollateral(base.RemoveCollateral):
    pass


class V1GoerliAddCollateral(base.AddCollateral):
    pass


class V1GoerliAddQuoteToken(base.AddQuoteToken):
    pass


class V1GoerliRemoveQuoteToken(base.RemoveQuoteToken):
    pass


class V1GoerliMoveQuoteToken(base.MoveQuoteToken):
    pass


class V1GoerliDrawDebt(base.DrawDebt):
    pass


class V1GoerliRepayDebt(base.RepayDebt):
    pass


class V1GoerliLiquidationAuction(base.LiquidationAuction):
    pass


class V1GoerliPoolVolumeSnapshot(base.PoolVolumeSnapshot):
    pass


class V1GoerliCurrentWalletPoolPosition(base.CurrentWalletPoolPosition):
    pass


class V1GoerliGrantProposal(base.GrantProposal):
    pass


class V1GoerliPoolEvent(base.PoolEvent):
    pass
