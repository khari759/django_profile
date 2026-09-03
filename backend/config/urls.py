"""Root URL configuration."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.views.decorators.http import require_GET


@require_GET
def api_root(request):
    """Landing response so hitting the bare backend host is not a 404."""
    return JsonResponse(
        {
            "name": "Portfolio API",
            "docs": "/api/",
            "admin": "/admin/",
            "endpoints": [
                "/api/overview/",
                "/api/profile/",
                "/api/skills/",
                "/api/experience/",
                "/api/projects/",
                "/api/education/",
                "/api/certifications/",
                "/api/contact/",
                "/api/health/",
            ],
        }
    )


urlpatterns = [
    path("", api_root, name="api-root"),
    path("admin/", admin.site.urls),
    path("api/", include("portfolio.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
