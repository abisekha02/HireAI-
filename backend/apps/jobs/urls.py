from rest_framework.routers import DefaultRouter

from .views import JobPostingViewSet

router = DefaultRouter()
router.register("", JobPostingViewSet, basename="job")

urlpatterns = router.urls
