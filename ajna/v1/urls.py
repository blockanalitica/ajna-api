from django.urls import path

from .views import (
    auctions,
    grants,
    pool,
    pools,
    positions,
    search,
    stats,
    token,
    tokens,
    wallet,
)

urlpatterns = [
    path(
        "pools/",
        pools.PoolsView.as_view(),
        name="pools",
    ),
    path(
        "pools/<pool_address>/",
        pool.PoolView.as_view(),
        name="pool",
    ),
    path(
        "pools/<pool_address>/buckets/",
        pool.BucketsView.as_view(),
        name="pool-buckets",
    ),
    path(
        "pools/<pool_address>/buckets/graph/",
        pool.BucketsGraphView.as_view(),
        name="pool-buckets-graph",
    ),
    path(
        "pools/<pool_address>/historic/<historic_type>/",
        pool.PoolHistoricView.as_view(),
        name="pool-historic",
    ),
    path(
        "pools/<pool_address>/events/",
        pool.PoolEventsView.as_view(),
        name="pool-events",
    ),
    path(
        "pools/<pool_address>/borrowers/",
        pool.PoolBorrowersView.as_view(),
        name="pool-borrowers",
    ),
    path(
        "pools/<pool_address>/lenders/",
        pool.PoolLendersView.as_view(),
        name="pool-lenders",
    ),
    path(
        "tokens/",
        tokens.TokensView.as_view(),
        name="tokens",
    ),
    path(
        "tokens/<underlying_address>/",
        token.TokenView.as_view(),
        name="token",
    ),
    path(
        "tokens/<underlying_address>/overview/",
        token.TokenOverviewView.as_view(),
        name="token-overview",
    ),
    path(
        "tokens/<underlying_address>/pools/",
        token.TokenPoolsView.as_view(),
        name="token-pools",
    ),
    path(
        "tokens/<underlying_address>/arbitrage-pools/",
        token.TokenArbitragePoolsView.as_view(),
        name="token-arbitrage-pools",
    ),
    path(
        "stats/overview/",
        stats.OverviewView.as_view(),
        name="overview",
    ),
    path(
        "search/",
        search.SearchView.as_view(),
        name="search",
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
        "grants/funding-proposals/",
        grants.FundingProposalsView.as_view(),
        name="grands-funding-proposals",
    ),
    path(
        "grants/finalize-proposals/",
        grants.FinalizeProposalsView.as_view(),
        name="grands-finalize-proposals",
    ),
    # URLS that we use internally
    path(
        "pools/<pool_address>/borrowers-csv/",
        pool.PoolBorrowersCsvView.as_view(),
        name="pool-borrowers-csv",
    ),
    path(
        "pools/<pool_address>/lenders-csv/",
        pool.PoolLendersCsvView.as_view(),
        name="pool-lenders-csv",
    ),
    path(
        "positions/",
        positions.PositionsView.as_view(),
        name="positions",
    ),
    path(
        "wallets/<wallet_address>/positions/",
        wallet.WalletPositionsView.as_view(),
        name="wallet-positions",
    ),
    path(
        "wallets/<wallet_address>/events/",
        wallet.WalletEventsView.as_view(),
        name="wallet-events",
    ),

    path(
        "pools/<pool_address>/events1337/",
        wallet.PoolEventsView.as_view(),
        name="pool-events-1337",
    ),
]
