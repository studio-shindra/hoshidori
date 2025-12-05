# api/admin.py
from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ManyToManyWidget, ForeignKeyWidget
from django.utils.text import slugify

from .models import Theater, Actor, Troupe, Work, Run, ViewingLog, Tag


# ===== カスタム Widget =====

class TheaterWidget(ForeignKeyWidget):
    """
    Works CSV の main_theater カラムから Theater を自動で get_or_create する Widget。
    """
    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return None
        name = value.strip()
        obj, _ = Theater.objects.get_or_create(name=name)
        return obj


class TroupeWidget(ForeignKeyWidget):
    """
    Works CSV の troupe カラムから Troupe を自動で get_or_create する Widget。
    """
    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return None
        name = value.strip()
        if not name:
            return None
        slug = slugify(name)
        troupe, _ = Troupe.objects.get_or_create(
            name=name,
            defaults={"slug": slug},
        )
        return troupe


class ActorWidget(ManyToManyWidget):
    """
    Works CSV の actors カラム（例: "俳優A, 俳優B"）から
    Actor を自動で get_or_create して紐づける Widget。
    """
    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return []
        names = [name.strip() for name in value.split(',') if name.strip()]
        actors = []
        for name in names:
            obj, _ = Actor.objects.get_or_create(name=name)
            actors.append(obj)
        return actors


# ===== Theater =====

class TheaterResource(resources.ModelResource):
    class Meta:
        model = Theater
        fields = ('id', 'name', 'slug', 'area', 'address', 'image_url', 'area_tags')


@admin.register(Theater)
class TheaterAdmin(ImportExportModelAdmin):
    resource_class = TheaterResource
    list_display = ('name', 'area', 'area_tags_display', 'slug')
    search_fields = ('name', 'slug', 'area', 'area_tags')

    @admin.display(description='エリアタグ')
    def area_tags_display(self, obj: Theater) -> str:
        if not obj.area_tags:
            return ''
        return ', '.join(obj.area_tags)


# ===== Tag =====

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# ===== Actor =====

@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# ===== Troupe =====

class TroupeResource(resources.ModelResource):
    class Meta:
        model = Troupe
        fields = ('id', 'name', 'slug', 'official_site', 'image_allowed')


@admin.register(Troupe)
class TroupeAdmin(ImportExportModelAdmin):
    resource_class = TroupeResource
    list_display = ('name', 'slug', 'image_allowed', 'official_site')
    list_filter = ('image_allowed',)
    search_fields = ('name', 'slug', 'official_site')
    list_editable = ('image_allowed',)  # リスト画面で直接編集可能


# ===== Work =====

class WorkResource(resources.ModelResource):
    """
    Works 用のインポート／エクスポート Resource。
    main_theater / troupe / actors / tags を名前ベースで処理する。
    """

    main_theater = fields.Field(
        column_name='main_theater',
        attribute='main_theater',
        widget=TheaterWidget(Theater, 'name'),
    )

    troupe = fields.Field(
        column_name='troupe',
        attribute='troupe',
        widget=TroupeWidget(Troupe, 'name'),
    )

    actors = fields.Field(
        column_name='actors',
        attribute='actors',
        widget=ActorWidget(Actor, field='name', separator=','),
    )

    tags = fields.Field(
        column_name='tags',
        attribute='tags',
        widget=ManyToManyWidget(Tag, field='name', separator=','),
    )

    class Meta:
        model = Work
        fields = (
            'id',
            'title',
            'slug',
            'troupe',
            'main_theater',
            'actors',
            'status',
            'tags',
        )


class RunInline(admin.TabularInline):
    model = Run
    extra = 0


@admin.register(Work)
class WorkAdmin(ImportExportModelAdmin):
    resource_class = WorkResource
    list_display = ('title', 'troupe', 'main_theater', 'status', 'is_quick_created', 'created_at')
    list_filter = ('status', 'is_quick_created', 'main_theater', 'troupe')
    search_fields = ('title', 'troupe__name', 'tags__name')
    filter_horizontal = ('actors', 'tags')
    inlines = [RunInline]


# ===== Run =====

class RunResource(resources.ModelResource):
    class Meta:
        model = Run
        fields = (
            'id',
            'work',
            'label',
            'area',
            'theater',
            'start_date',
            'end_date',
        )


@admin.register(Run)
class RunAdmin(ImportExportModelAdmin):
    resource_class = RunResource
    list_display = ('work', 'label', 'area', 'theater', 'start_date', 'end_date')
    list_filter = ('area', 'theater', 'work')
    search_fields = ('work__title', 'label')



# ===== ViewingLog =====

@admin.register(ViewingLog)
class ViewingLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'work', 'watched_at', 'rating')  # watched_at に変えたならここも揃える
    list_filter = ('rating', 'work', 'user')
    search_fields = ('work__title', 'user__username', 'user__email', 'tags__name')
    autocomplete_fields = ('work', 'user', 'run')