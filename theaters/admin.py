from django.contrib import admin

from .models import Theater


@admin.register(Theater)
class TheaterAdmin(admin.ModelAdmin):
    list_display = ['name', 'prefecture', 'city', 'is_approved', 'is_active', 'created_by']
    list_filter = ['is_approved', 'is_active', 'prefecture', 'area_name']
    search_fields = ['name', 'area_name', 'address', 'google_place_id']
    prepopulated_fields = {'slug': ('name',)}
