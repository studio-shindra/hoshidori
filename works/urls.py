from rest_framework.routers import DefaultRouter

from .views import PerformanceCastViewSet, PerformanceViewSet, PersonViewSet, WorkViewSet

router = DefaultRouter()
router.register('works', WorkViewSet)
router.register('performances', PerformanceViewSet)
router.register('people', PersonViewSet)
router.register('casts', PerformanceCastViewSet)

urlpatterns = router.urls
