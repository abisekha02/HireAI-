from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import TokenRefreshView

from apps.users.views import LoginView, RegisterView, MeView

urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path("api/auth/login/", LoginView.as_view(), name="login"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/me/", MeView.as_view(), name="me"),
    # Feature apps
    path("api/jobs/", include("apps.jobs.urls")),
    path("api/resumes/", include("apps.resumes.urls")),
    path("api/applications/", include("apps.applications.urls")),
    path("api/interviews/", include("apps.interviews.urls")),
    path("api/evaluations/", include("apps.evaluations.urls")),
    path("api/matching/", include("apps.matching.urls")),
    # Schema / docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
