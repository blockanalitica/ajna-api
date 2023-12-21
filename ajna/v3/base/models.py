from ...models import base


class V3BasePool(base.Pool):
    pass


class V3BasePoolSnapshot(base.PoolSnapshot):
    pass


class V3BaseToken(base.Token):
    pass


class V3BaseBucket(base.Bucket):
    pass


class V3BasePriceFeed(base.PriceFeed):
    pass


class V3BasePoolVolumeSnapshot(base.PoolVolumeSnapshot):
    pass


class V3BasePoolEvent(base.PoolEvent):
    pass


class V3BaseCurrentWalletPoolPosition(base.CurrentWalletPoolPosition):
    pass


class V3BaseWalletPoolPosition(base.WalletPoolPosition):
    pass


class V3BasePoolBucketState(base.PoolBucketState):
    pass


class V3BaseWalletPoolBucketState(base.WalletPoolBucketState):
    pass


class V3BaseWallet(base.Wallet):
    pass


class V3BaseNotification(base.Notification):
    pass


class V3BaseAuction(base.Auction):
    pass


class V3BaseAuctionKick(base.AuctionKick):
    pass


class V3BaseAuctionTake(base.AuctionTake):
    pass


class V3BaseAuctionBucketTake(base.AuctionBucketTake):
    pass


class V3BaseAuctionSettle(base.AuctionSettle):
    pass


class V3BaseAuctionAuctionSettle(base.AuctionAuctionSettle):
    pass


class V3BaseAuctionAuctionNFTSettle(base.AuctionAuctionNFTSettle):
    pass


class V3BaseGrantDistributionPeriod(base.GrantDistributionPeriod):
    pass


class V3BaseGrantProposal(base.GrantProposal):
    pass


class V3BaseGrantEvent(base.GrantEvent):
    pass


class V3BaseReserveAuction(base.ReserveAuction):
    pass


class V3BaseReserveAuctionKick(base.ReserveAuctionKick):
    pass


class V3BaseReserveAuctionTake(base.ReserveAuctionTake):
    pass
