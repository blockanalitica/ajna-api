import copy

from django.urls import path

from ..urls import urlpatterns as base_patterns
from ..views import grants

app_name = "v3_ethereum"

urlpatterns = copy.deepcopy(base_patterns)
urlpatterns += [
    path(
        "grants/",
        grants.GrantsView.as_view(),
        name="grants",
    ),
]
