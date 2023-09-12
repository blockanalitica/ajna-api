from django.urls import path

from .views import pool, pools

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
]
