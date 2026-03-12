from rest_framework.routers import DefaultRouter

from .views import CouponViewSet, ShopViewSet

router = DefaultRouter()
router.register('shops', ShopViewSet)
router.register('coupons', CouponViewSet)

urlpatterns = router.urls
