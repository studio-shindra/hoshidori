from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkViewSet, ViewingLogViewSet, TheaterViewSet, ActorViewSet, TroupeViewSet, register

router = DefaultRouter()
router.register(r'works', WorkViewSet, basename='work')
router.register(r'logs', ViewingLogViewSet, basename='log')
router.register(r'theaters', TheaterViewSet, basename='theater')
router.register(r'actors', ActorViewSet, basename='actor')
router.register(r'troupes', TroupeViewSet, basename='troupe')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', register),
]