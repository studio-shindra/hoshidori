from django.contrib import admin

from .models import Theater


@admin.register(Theater)
class TheaterAdmin(admin.ModelAdmin):
    list_display = ['name', 'area_name', 'nearest_station', 'is_active']
    list_filter = ['is_active', 'area_name']
    search_fields = ['name', 'area_name']
    prepopulated_fields = {'slug': ('name',)}
