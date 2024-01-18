"""
NOTE: v4 of ethereum is the same as v3!
They've redeployed only L2s for the v4 version.
"""

from ...models import base


class V3EthereumPool(base.Pool):
    pass


class V3EthereumPoolSnapshot(base.PoolSnapshot):
    pass


class V3EthereumToken(base.Token):
    pass


class V3EthereumBucket(base.Bucket):
    pass


class V3EthereumPriceFeed(base.PriceFeed):
    pass


class V3EthereumPoolVolumeSnapshot(base.PoolVolumeSnapshot):
    pass


class V3EthereumPoolEvent(base.PoolEvent):
    pass


class V3EthereumCurrentWalletPoolPosition(base.CurrentWalletPoolPosition):
    pass


class V3EthereumWalletPoolPosition(base.WalletPoolPosition):
    pass


class V3EthereumPoolBucketState(base.PoolBucketState):
    pass


class V3EthereumWalletPoolBucketState(base.WalletPoolBucketState):
    pass


class V3EthereumWallet(base.Wallet):
    pass


class V3EthereumNotification(base.Notification):
    pass


class V3EthereumAuction(base.Auction):
    pass


class V3EthereumAuctionKick(base.AuctionKick):
    pass


class V3EthereumAuctionTake(base.AuctionTake):
    pass


class V3EthereumAuctionBucketTake(base.AuctionBucketTake):
    pass


class V3EthereumAuctionSettle(base.AuctionSettle):
    pass


class V3EthereumAuctionAuctionSettle(base.AuctionAuctionSettle):
    pass


class V3EthereumAuctionAuctionNFTSettle(base.AuctionAuctionNFTSettle):
    pass


class V3EthereumGrantDistributionPeriod(base.GrantDistributionPeriod):
    pass


class V3EthereumGrantProposal(base.GrantProposal):
    pass


class V3EthereumGrantEvent(base.GrantEvent):
    pass


class V3EthereumReserveAuction(base.ReserveAuction):
    pass


class V3EthereumReserveAuctionKick(base.ReserveAuctionKick):
    pass


class V3EthereumReserveAuctionTake(base.ReserveAuctionTake):
    pass
