from django.urls import path
from rest_framework.routers import DefaultRouter

from .dashboard_views import (
    ShopApplicationView, ShopBillingPortalView, ShopCheckoutView,
    ShopDashboardView, ShopImageUploadView, ShopPlaceCandidateView,
    StripeWebhookView,
)
from .views import ShopViewSet

router = DefaultRouter()
router.register('shops', ShopViewSet)

urlpatterns = [
    path('shop-application/', ShopApplicationView.as_view(), name='shop-application'),
    path('shop-place-candidates/', ShopPlaceCandidateView.as_view(), name='shop-place-candidates'),
    path('dashboard/', ShopDashboardView.as_view(), name='shop-dashboard'),
    path('dashboard/image/', ShopImageUploadView.as_view(), name='shop-dashboard-image'),
    path('dashboard/checkout/', ShopCheckoutView.as_view(), name='shop-dashboard-checkout'),
    path('dashboard/billing-portal/', ShopBillingPortalView.as_view(), name='shop-dashboard-billing-portal'),
    path('stripe/webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
] + router.urls
