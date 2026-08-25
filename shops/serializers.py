from rest_framework import serializers

from .models import Shop


class ShopSerializer(serializers.ModelSerializer):
    image_src = serializers.SerializerMethodField()
    is_want_to_go = serializers.SerializerMethodField()
    after_viewing_count = serializers.IntegerField(read_only=True, default=0)
    listing_tier = serializers.SerializerMethodField()

    class Meta:
        model = Shop
        fields = [
            'id', 'name', 'slug', 'category', 'description',
            'address', 'nearest_station', 'distance_note',
            'website_url', 'instagram_url', 'tabelog_url', 'google_map_url',
            'phone_number', 'opening_hours_text', 'benefit_text',
            'image_url', 'image_src', 'after_viewing_count',
            'listing_tier',
            'is_featured', 'is_active', 'created_at', 'updated_at',
            'is_want_to_go',
        ]

    def get_is_want_to_go(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        if hasattr(obj, '_is_want_to_go'):
            return obj._is_want_to_go
        return obj.want_to_go.filter(user=request.user).exists()

    def get_image_src(self, obj):
        if obj.image_url:
            return obj.image_url
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def get_listing_tier(self, obj):
        if obj.is_featured or getattr(obj, '_has_featured_link', False):
            return 'sponsored'
        if getattr(obj, '_has_recognized_link', False):
            return 'recognized'
        return 'standard'
