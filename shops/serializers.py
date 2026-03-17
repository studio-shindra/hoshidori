from rest_framework import serializers

from .models import Coupon, CouponUseLog, Shop


class ShopSerializer(serializers.ModelSerializer):
    image_src = serializers.SerializerMethodField()
    coupon_text = serializers.SerializerMethodField()

    class Meta:
        model = Shop
        fields = [
            'id', 'name', 'slug', 'category', 'description',
            'address', 'nearest_station', 'distance_note',
            'website_url', 'instagram_url', 'tabelog_url', 'google_map_url',
            'phone_number', 'opening_hours_text', 'benefit_text',
            'image_url', 'image_src', 'coupon_text',
            'is_featured', 'is_active', 'created_at', 'updated_at',
        ]

    def get_coupon_text(self, obj):
        coupons = getattr(obj, '_prefetched_active_coupons', None)
        if coupons is not None:
            coupon = coupons[0] if coupons else None
        else:
            coupon = obj.coupons.filter(is_active=True).first()
        if coupon:
            return coupon.discount_text or coupon.title
        return None

    def get_image_src(self, obj):
        if obj.image_url:
            return obj.image_url
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


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
