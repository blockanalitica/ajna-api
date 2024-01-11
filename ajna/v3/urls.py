from django.urls import path

from .views import (  # grants,
    auctions,
    notifications,
    pools,
    reserve_auctions,
    search,
    stats,
    tokens,
    wallets,
)

urlpatterns = [
    path(
        "pools/",
        pools.PoolsView.as_view(),
        name="pools",
    ),
    path(
        "pools/<pool_address>/",
        pools.PoolView.as_view(),
        name="pool",
    ),
    path(
        "pools/<pool_address>/positions/",
        pools.PoolPositionsView.as_view(),
        name="pool-positions",
    ),
    path(
        "pools/<pool_address>/buckets/graph/",
        pools.BucketsGraphView.as_view(),
        name="pool-buckets-graph",
    ),
    path(
        "pools/<pool_address>/buckets/list/",
        pools.BucketsListView.as_view(),
        name="pool-buckets-list",
    ),
    path(
        "pools/<pool_address>/buckets/<bucket_index>/",
        pools.BucketView.as_view(),
        name="pool-bucket",
    ),
    path(
        "pools/<pool_address>/buckets/<bucket_index>/depositors/",
        pools.BucketDepositorsView.as_view(),
        name="pool-bucket-depositors",
    ),
    path(
        "pools/<pool_address>/buckets/<bucket_index>/historic/",
        pools.BucketHistoricView.as_view(),
        name="pool-bucket-historic",
    ),
    path(
        "pools/<pool_address>/buckets/<bucket_index>/events/",
        pools.BucketEventsView.as_view(),
        name="pool-bucket-events",
    ),
    path(
        "pools/<pool_address>/historic/<historic_type>/",
        pools.PoolHistoricView.as_view(),
        name="pool-historic",
    ),
    path(
        "pools/<pool_address>/events/",
        pools.PoolEventsView.as_view(),
        name="pool-events",
    ),
    path(
        "pools/<pool_address>/auctions/settled/",
        pools.AuctionsSettledView.as_view(),
        name="pools-auctions-settled",
    ),
    path(
        "pools/<pool_address>/auctions/active/",
        pools.AuctionsActiveView.as_view(),
        name="pools-auctions-active",
    ),
    path(
        "pools/<pool_address>/auctions/to-kick/",
        pools.AuctionsToKickView.as_view(),
        name="pools-auctions-to-kick",
    ),
    path(
        "pools/<pool_address>/reserve-auctions/expired/",
        pools.PoolReserveAuctionsExpiredView.as_view(),
        name="pools-reserve-auctions-expired",
    ),
    path(
        "pools/<pool_address>/reserve-auctions/active/",
        pools.PoolReserveAuctionsActiveView.as_view(),
        name="pools-reserve-auctions-active",
    ),
    path(
        "pools/<pool_address>/at-risk/",
        pools.PoolAtRiskView.as_view(),
        name="pool-at-risk",
    ),
    path(
        "tokens/",
        tokens.TokensView.as_view(),
        name="tokens",
    ),
    path(
        "tokens/<underlying_address>/",
        tokens.TokenView.as_view(),
        name="token",
    ),
    path(
        "tokens/<underlying_address>/overview/",
        tokens.TokenOverviewView.as_view(),
        name="token-overview",
    ),
    path(
        "tokens/<underlying_address>/pools/",
        tokens.TokenPoolsView.as_view(),
        name="token-pools",
    ),
    path(
        "tokens/<underlying_address>/arbitrage-pools/",
        tokens.TokenArbitragePoolsView.as_view(),
        name="token-arbitrage-pools",
    ),
    path(
        "stats/overview/",
        stats.OverviewView.as_view(),
        name="overview",
    ),
    path(
        "stats/history/",
        stats.HistoryView.as_view(),
        name="stats-history",
    ),
    path(
        "search/",
        search.SearchView.as_view(),
        name="search",
    ),
    path(
        "wallets/",
        wallets.WalletsView.as_view(),
        name="wallets",
    ),
    path(
        "wallets/at-risk/",
        wallets.WalletsAtRiskView.as_view(),
        name="wallets-at-risk",
    ),
    path(
        "wallets/<address>/",
        wallets.WalletView.as_view(),
        name="wallet",
    ),
    path(
        "wallets/<address>/pools/",
        wallets.WalletPoolsView.as_view(),
        name="wallet-pools",
    ),
    path(
        "wallets/<address>/pools/<pool_address>/",
        wallets.WalletPoolView.as_view(),
        name="wallet-pool",
    ),
    path(
        "wallets/<address>/pools/<pool_address>/historic/",
        wallets.WalletPoolHistoricView.as_view(),
        name="wallet-pool-historic",
    ),
    path(
        "wallets/<address>/pools/<pool_address>/events/",
        wallets.WalletPoolEventsView.as_view(),
        name="wallet-pool-events",
    ),
    path(
        "wallets/<address>/pools/<pool_address>/buckets/",
        wallets.WalletPoolBucketsView.as_view(),
        name="wallet-pool-buckets",
    ),
    path(
        "wallets/<address>/events/",
        wallets.WalletEventsView.as_view(),
        name="wallet-events",
    ),
    path(
        "wallets/<address>/activity-heatmap/",
        wallets.WalletActivityHeatmapView.as_view(),
        name="wallet-activity-heatmap",
    ),
    path(
        "notifications/",
        notifications.NotificationsView.as_view(),
        name="notifications",
    ),
    path(
        "auctions/settled/",
        auctions.AuctionsSettledView.as_view(),
        name="auctions-settled",
    ),
    path(
        "auctions/settled/overview/",
        auctions.AuctionsSettledOverviewView.as_view(),
        name="auctions-settled-overview",
    ),
    path(
        "auctions/settled/graphs/<graph_type>/",
        auctions.AuctionsSettledGraphsView.as_view(),
        name="auctions-settled-graphs",
    ),
    path(
        "auctions/active/",
        auctions.AuctionsActiveView.as_view(),
        name="auctions-active",
    ),
    path(
        "auctions/to-kick/",
        auctions.AuctionsToKickView.as_view(),
        name="auctions-to-kick",
    ),
    path(
        "auctions/<uid>/",
        auctions.AuctionView.as_view(),
        name="auction",
    ),
    path(
        "auctions/<auction_uid>/events/",
        auctions.AuctionEventsView.as_view(),
        name="auction-events",
    ),
    path(
        "reserve-auctions/active/",
        reserve_auctions.ReserveAuctionsActiveView.as_view(),
        name="reserve-auctions-active",
    ),
    path(
        "reserve-auctions/expired/",
        reserve_auctions.ReserveAuctionsExpiredView.as_view(),
        name="reserve-auctions-expired",
    ),
    path(
        "reserve-auctions/<uid>/",
        reserve_auctions.ReserveAuctionView.as_view(),
        name="reserve-auction",
    ),
    path(
        "reserve-auctions/<uid>/events/",
        reserve_auctions.ReserveAuctionEventsView.as_view(),
        name="reserve-auction-events",
    ),
]
