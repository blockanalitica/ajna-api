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
]
