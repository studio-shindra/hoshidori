from rest_framework.routers import DefaultRouter

from .views import ReviewViewSet, ViewingLogViewSet

router = DefaultRouter()
router.register('reviews', ReviewViewSet, basename='review')
router.register('viewing-logs', ViewingLogViewSet, basename='viewing-log')

urlpatterns = router.urls
