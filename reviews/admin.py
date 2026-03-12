from django.contrib import admin

from .models import Review, ViewingLog


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'performance', 'rating_overall', 'is_spoiler', 'created_at']
    list_filter = ['is_spoiler', 'rating_overall']
    search_fields = ['body', 'title']


@admin.register(ViewingLog)
class ViewingLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'performance', 'watched_on', 'created_at']
    list_filter = ['watched_on']
