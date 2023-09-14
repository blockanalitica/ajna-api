from django.urls import path

from .views import pools

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
        "pools/<pool_address>/buckets/",
        pools.BucketsView.as_view(),
        name="pool-buckets",
    ),
    path(
        "pools/<pool_address>/buckets/graph/",
        pools.BucketsGraphView.as_view(),
        name="pool-buckets-graph",
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
]
