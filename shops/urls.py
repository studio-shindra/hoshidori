from django.urls import path
from rest_framework.routers import DefaultRouter

from .dashboard_views import ShopDashboardView
from .views import ShopViewSet

router = DefaultRouter()
router.register('shops', ShopViewSet)

urlpatterns = [
    path('dashboard/', ShopDashboardView.as_view(), name='shop-dashboard'),
] + router.urls
