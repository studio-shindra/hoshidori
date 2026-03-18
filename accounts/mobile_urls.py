from django.urls import path

from . import mobile_views

urlpatterns = [
    path('auth/register/', mobile_views.MobileRegisterView.as_view(), name='mobile-register'),
    path('auth/login/', mobile_views.MobileLoginView.as_view(), name='mobile-login'),
    path('auth/logout/', mobile_views.MobileLogoutView.as_view(), name='mobile-logout'),
    path('auth/me/', mobile_views.MobileMeView.as_view(), name='mobile-me'),
]
