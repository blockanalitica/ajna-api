from ...models import base


class V4HemiPool(base.Pool):
    pass


class V4HemiPoolSnapshot(base.PoolSnapshot):
    pass


class V4HemiToken(base.Token):
    pass


class V4HemiBucket(base.Bucket):
    pass


class V4HemiPriceFeed(base.PriceFeed):
    pass


class V4HemiPoolVolumeSnapshot(base.PoolVolumeSnapshot):
    pass


class V4HemiPoolEvent(base.PoolEvent):
    pass


class V4HemiCurrentWalletPoolPosition(base.CurrentWalletPoolPosition):
    pass


class V4HemiWalletPoolPosition(base.WalletPoolPosition):
    pass


class V4HemiPoolBucketState(base.PoolBucketState):
    pass


class V4HemiWalletPoolBucketState(base.WalletPoolBucketState):
    pass


class V4HemiWallet(base.Wallet):
    pass


class V4HemiNotification(base.Notification):
    pass


class V4HemiAuction(base.Auction):
    pass


class V4HemiAuctionKick(base.AuctionKick):
    pass


class V4HemiAuctionTake(base.AuctionTake):
    pass


class V4HemiAuctionBucketTake(base.AuctionBucketTake):
    pass


class V4HemiAuctionSettle(base.AuctionSettle):
    pass


class V4HemiAuctionAuctionSettle(base.AuctionAuctionSettle):
    pass


class V4HemiAuctionAuctionNFTSettle(base.AuctionAuctionNFTSettle):
    pass


class V4HemiReserveAuction(base.ReserveAuction):
    pass


class V4HemiReserveAuctionKick(base.ReserveAuctionKick):
    pass


class V4HemiReserveAuctionTake(base.ReserveAuctionTake):
    pass


class V4HemiActivitySnapshot(base.ActivitySnapshot):
    pass
