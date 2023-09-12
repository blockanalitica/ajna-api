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
]
