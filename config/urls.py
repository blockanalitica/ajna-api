from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views import defaults as default_views
from django.views.generic import RedirectView


def trigger_error(request):
    division_by_zero = 1 / 0
    return division_by_zero


urlpatterns = [
    path("admin/", admin.site.urls),
    path("sentry-debug/", trigger_error),
    path("v2/ethereum/", include("ajna.v2.ethereum.urls")),
    re_path(
        r"^v3/ethereum/(?P<rest>.*)",
        RedirectView.as_view(url="/v4/ethereum/%(rest)s", permanent=False, query_string=True),
    ),
    path("v3/base/", include("ajna.v3.base.urls")),
    path("v3/arbitrum/", include("ajna.v3.arbitrum.urls")),
    path("v3/optimism/", include("ajna.v3.optimism.urls")),
    path("v3/polygon/", include("ajna.v3.polygon.urls")),
    path("v4/overall/", include("ajna.v4.views.overall")),
    path("v4/ethereum/", include("ajna.v4.ethereum.urls")),
    path("v4/base/", include("ajna.v4.base.urls")),
    path("v4/arbitrum/", include("ajna.v4.arbitrum.urls")),
    path("v4/optimism/", include("ajna.v4.optimism.urls")),
    path("v4/polygon/", include("ajna.v4.polygon.urls")),
    path("v4/blast/", include("ajna.v4.blast.urls")),
    path("v4/gnosis/", include("ajna.v4.gnosis.urls")),
    path("v4/mode/", include("ajna.v4.mode.urls")),
    path("v4/rari/", include("ajna.v4.rari.urls")),
    path("v4/avalanche/", include("ajna.v4.avalanche.urls")),
    path("v4/linea/", include("ajna.v4.linea.urls")),
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls)), *urlpatterns]
