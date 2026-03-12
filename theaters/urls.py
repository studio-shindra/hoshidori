from rest_framework.routers import DefaultRouter

from .views import TheaterViewSet

router = DefaultRouter()
router.register('theaters', TheaterViewSet)

urlpatterns = router.urls
