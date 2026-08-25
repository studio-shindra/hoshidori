from rest_framework.routers import DefaultRouter

from .views import ReviewViewSet, UserBlockViewSet, ViewingLogViewSet

router = DefaultRouter()
router.register('reviews', ReviewViewSet, basename='review')
router.register('viewing-logs', ViewingLogViewSet, basename='viewing-log')
router.register('user-blocks', UserBlockViewSet, basename='user-block')

urlpatterns = router.urls
