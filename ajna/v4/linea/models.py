from ...models import base


class V4LineaPool(base.Pool):
    pass


class V4LineaPoolSnapshot(base.PoolSnapshot):
    pass


class V4LineaToken(base.Token):
    pass


class V4LineaBucket(base.Bucket):
    pass


class V4LineaPriceFeed(base.PriceFeed):
    pass


class V4LineaPoolVolumeSnapshot(base.PoolVolumeSnapshot):
    pass


class V4LineaPoolEvent(base.PoolEvent):
    pass


class V4LineaCurrentWalletPoolPosition(base.CurrentWalletPoolPosition):
    pass


class V4LineaWalletPoolPosition(base.WalletPoolPosition):
    pass


class V4LineaPoolBucketState(base.PoolBucketState):
    pass


class V4LineaWalletPoolBucketState(base.WalletPoolBucketState):
    pass


class V4LineaWallet(base.Wallet):
    pass


class V4LineaNotification(base.Notification):
    pass


class V4LineaAuction(base.Auction):
    pass


class V4LineaAuctionKick(base.AuctionKick):
    pass


class V4LineaAuctionTake(base.AuctionTake):
    pass


class V4LineaAuctionBucketTake(base.AuctionBucketTake):
    pass


class V4LineaAuctionSettle(base.AuctionSettle):
    pass


class V4LineaAuctionAuctionSettle(base.AuctionAuctionSettle):
    pass


class V4LineaAuctionAuctionNFTSettle(base.AuctionAuctionNFTSettle):
    pass


class V4LineaReserveAuction(base.ReserveAuction):
    pass


class V4LineaReserveAuctionKick(base.ReserveAuctionKick):
    pass


class V4LineaReserveAuctionTake(base.ReserveAuctionTake):
    pass


class V4LineaActivitySnapshot(base.ActivitySnapshot):
    pass
