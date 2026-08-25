from django.contrib import admin
from django.utils import timezone

from .models import (
    PerformanceCast, Performance, Person, PosterSubmission, Work,
    WorkEditProposal,
)


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


@admin.action(description='選択した提案を反映する')
def approve_proposals(modeladmin, request, queryset):
    for proposal in queryset.filter(status='pending').select_related('work', 'performance'):
        if proposal.performance_id:
            changes = dict(proposal.changes)
            if 'theater' in changes:
                changes['theater_id'] = changes.pop('theater')
            Performance.objects.filter(pk=proposal.performance_id).update(**changes)
        else:
            Work.objects.filter(pk=proposal.work_id).update(**proposal.changes)
        proposal.status = 'approved'
        proposal.reviewed_at = timezone.now()
        proposal.save(update_fields=['status', 'reviewed_at'])


@admin.action(description='選択した提案を見送る')
def reject_proposals(modeladmin, request, queryset):
    queryset.filter(status='pending').update(status='rejected', reviewed_at=timezone.now())


@admin.register(WorkEditProposal)
class WorkEditProposalAdmin(admin.ModelAdmin):
    list_display = ['work', 'performance', 'proposed_by', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['work__title', 'performance__theater__name', 'proposed_by__username']
    readonly_fields = ['work', 'performance', 'proposed_by', 'changes', 'created_at', 'reviewed_at']
    actions = [approve_proposals, reject_proposals]
