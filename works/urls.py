from rest_framework.routers import DefaultRouter

from .views import PerformanceViewSet, PersonViewSet, WorkViewSet

router = DefaultRouter()
router.register('works', WorkViewSet)
router.register('performances', PerformanceViewSet)
router.register('people', PersonViewSet)

urlpatterns = router.urls
