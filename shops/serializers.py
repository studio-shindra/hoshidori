from rest_framework import serializers

from .models import Coupon, CouponUseLog, Shop


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = [
            'id', 'name', 'slug', 'category', 'description',
            'address', 'nearest_station', 'distance_note',
            'website_url', 'instagram_url', 'tabelog_url', 'google_map_url',
            'phone_number', 'opening_hours_text', 'benefit_text',
            'is_active', 'created_at', 'updated_at',
        ]


class CouponSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.name', read_only=True)

    class Meta:
        model = Coupon
        fields = [
            'id', 'shop', 'shop_name', 'title', 'description',
            'discount_text', 'conditions',
            'start_date', 'end_date', 'is_active', 'created_at',
        ]


class CouponUseLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CouponUseLog
        fields = ['id', 'coupon', 'user', 'performance', 'used_at']
        read_only_fields = ['id', 'user', 'used_at']
