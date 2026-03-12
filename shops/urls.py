from django.urls import path
from rest_framework.routers import DefaultRouter

from .dashboard_views import ShopDashboardView
from .views import CouponViewSet, ShopViewSet

router = DefaultRouter()
router.register('shops', ShopViewSet)
router.register('coupons', CouponViewSet)

urlpatterns = [
    path('dashboard/', ShopDashboardView.as_view(), name='shop-dashboard'),
] + router.urls
