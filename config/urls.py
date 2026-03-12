from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('theaters.urls')),
    path('api/', include('works.urls')),
    path('api/', include('reviews.urls')),
]
