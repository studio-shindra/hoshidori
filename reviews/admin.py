from django.contrib import admin

from .models import Like, Review, ReviewReport, UserBlock, ViewingLog, ViewingLogImage


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'performance', 'rating_overall', 'is_spoiler', 'created_at']
    list_filter = ['is_spoiler', 'rating_overall']
    search_fields = ['body', 'title']


@admin.register(ViewingLog)
class ViewingLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'performance', 'status', 'watched_on', 'created_at']
    list_filter = ['status', 'watched_on']


@admin.register(ViewingLogImage)
class ViewingLogImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'viewing_log', 'order', 'created_at']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'review', 'created_at']
    list_filter = ['created_at']


@admin.register(ReviewReport)
class ReviewReportAdmin(admin.ModelAdmin):
    list_display = ['review', 'reporter', 'reason', 'status', 'created_at']
    list_filter = ['reason', 'status', 'created_at']
    search_fields = ['review__body', 'reporter__username', 'details']


@admin.register(UserBlock)
class UserBlockAdmin(admin.ModelAdmin):
    list_display = ['blocker', 'blocked', 'created_at']
    search_fields = ['blocker__username', 'blocked__username']
