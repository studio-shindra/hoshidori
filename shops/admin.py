from django.contrib import admin

from .models import (
    Coupon, CouponUseLog, Shop, ShopClickLog,
    ShopPlan, ShopSubscription, ShopWantToGo, TheaterShop,
)


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'category', 'application_status', 'is_active', 'is_featured', 'featured_order', 'created_at']
    list_filter = ['is_active', 'category', 'is_featured']
    list_editable = ['is_featured', 'featured_order']
    search_fields = ['name', 'address', 'google_place_id', 'owner__username', 'owner__email']
    prepopulated_fields = {'slug': ('name',)}
    actions = ['approve_free_listing', 'mark_recommended', 'remove_recommended']

    @admin.display(description='状態')
    def application_status(self, obj):
        if not obj.is_active:
            return '申請中'
        return 'おすすめ店' if obj.is_featured else '無料掲載'

    @admin.action(description='選択した申請を無料掲載として承認')
    def approve_free_listing(self, request, queryset):
        queryset.update(is_active=True, is_featured=False)

    @admin.action(description='選択した店舗をおすすめ店にする')
    def mark_recommended(self, request, queryset):
        queryset.update(is_active=True, is_featured=True)

    @admin.action(description='選択した店舗を無料掲載に戻す')
    def remove_recommended(self, request, queryset):
        queryset.update(is_featured=False)


@admin.register(TheaterShop)
class TheaterShopAdmin(admin.ModelAdmin):
    list_display = ['theater', 'shop', 'sort_order', 'is_featured', 'is_recognized']
    list_filter = ['is_featured', 'is_recognized']
    list_editable = ['sort_order', 'is_featured', 'is_recognized']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['title', 'shop', 'discount_text', 'is_active', 'start_date', 'end_date']
    list_filter = ['is_active', 'shop']


@admin.register(CouponUseLog)
class CouponUseLogAdmin(admin.ModelAdmin):
    list_display = ['coupon', 'user', 'performance', 'used_at']
    list_filter = ['used_at']


@admin.register(ShopClickLog)
class ShopClickLogAdmin(admin.ModelAdmin):
    list_display = ['shop', 'user', 'source_type', 'clicked_target', 'created_at']
    list_filter = ['source_type', 'clicked_target']


@admin.register(ShopWantToGo)
class ShopWantToGoAdmin(admin.ModelAdmin):
    list_display = ['user', 'shop', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'shop__name']


@admin.register(ShopPlan)
class ShopPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'monthly_price', 'is_active']
    list_filter = ['is_active']


@admin.register(ShopSubscription)
class ShopSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['shop', 'plan', 'status', 'current_period_start', 'current_period_end']
    list_filter = ['status']
