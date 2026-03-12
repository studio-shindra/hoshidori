from django.contrib import admin

from .models import PerformanceCast, Performance, Person, PosterSubmission, Work


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'is_approved', 'created_at']
    list_filter = ['is_approved']
    search_fields = ['title']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['name', 'phonetic', 'created_by', 'is_approved']
    list_filter = ['is_approved']
    search_fields = ['name', 'phonetic']
    prepopulated_fields = {'slug': ('name',)}


class PerformanceCastInline(admin.TabularInline):
    model = PerformanceCast
    extra = 1


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ['work', 'theater', 'company_name', 'start_date', 'end_date', 'is_approved']
    list_filter = ['is_approved', 'start_date']
    search_fields = ['work__title', 'theater__name', 'company_name']
    inlines = [PerformanceCastInline]


@admin.register(PosterSubmission)
class PosterSubmissionAdmin(admin.ModelAdmin):
    list_display = ['work', 'user', 'is_selected', 'image_url', 'created_at']
    list_filter = ['is_selected']
    search_fields = ['work__title', 'user__username']
    readonly_fields = ['image_url', 'image_public_id', 'image_width', 'image_height', 'image_format']
