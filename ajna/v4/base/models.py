from ...models import base


class V4BasePool(base.Pool):
    pass


class V4BasePoolSnapshot(base.PoolSnapshot):
    pass


class V4BaseToken(base.Token):
    pass


class V4BaseBucket(base.Bucket):
    pass


class V4BasePriceFeed(base.PriceFeed):
    pass


class V4BasePoolVolumeSnapshot(base.PoolVolumeSnapshot):
    pass


class V4BasePoolEvent(base.PoolEvent):
    pass


class V4BaseCurrentWalletPoolPosition(base.CurrentWalletPoolPosition):
    pass


class V4BaseWalletPoolPosition(base.WalletPoolPosition):
    pass


class V4BasePoolBucketState(base.PoolBucketState):
    pass


class V4BaseWalletPoolBucketState(base.WalletPoolBucketState):
    pass


class V4BaseWallet(base.Wallet):
    pass


class V4BaseNotification(base.Notification):
    pass


class V4BaseAuction(base.Auction):
    pass


class V4BaseAuctionKick(base.AuctionKick):
    pass


class V4BaseAuctionTake(base.AuctionTake):
    pass


class V4BaseAuctionBucketTake(base.AuctionBucketTake):
    pass


class V4BaseAuctionSettle(base.AuctionSettle):
    pass


class V4BaseAuctionAuctionSettle(base.AuctionAuctionSettle):
    pass


class V4BaseAuctionAuctionNFTSettle(base.AuctionAuctionNFTSettle):
    pass


class V4BaseReserveAuction(base.ReserveAuction):
    pass


class V4BaseReserveAuctionKick(base.ReserveAuctionKick):
    pass


class V4BaseReserveAuctionTake(base.ReserveAuctionTake):
    pass


class V4BaseActivitySnapshot(base.ActivitySnapshot):
    pass
