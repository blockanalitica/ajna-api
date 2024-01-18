import copy

from django.urls import path

from ..urls import urlpatterns as base_patterns  # noqa
from ..views import grants

app_name = "v3_goerli"

urlpatterns = copy.deepcopy(base_patterns)
urlpatterns += [
    path(
        "grants/",
        grants.GrantsView.as_view(),
        name="grants",
    ),
]
