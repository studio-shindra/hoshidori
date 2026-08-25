from rest_framework import serializers

from .models import Shop


class ShopSerializer(serializers.ModelSerializer):
    image_src = serializers.SerializerMethodField()
    image_source = serializers.SerializerMethodField()
    google_photo_maps_uri = serializers.SerializerMethodField()
    google_photo_attributions = serializers.SerializerMethodField()
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
            'image_url', 'image_src', 'image_source',
            'google_photo_maps_uri', 'google_photo_attributions',
            'after_viewing_count',
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
        return self._google_place(obj).get('photo_uri') or None

    def get_image_source(self, obj):
        if obj.image_url or obj.image:
            return 'owned'
        if self._google_place(obj).get('photo_uri'):
            return 'google_places'
        return ''

    def get_google_photo_maps_uri(self, obj):
        place = self._google_place(obj)
        return place.get('photo_google_maps_uri') or place.get('google_maps_uri') or ''

    def get_google_photo_attributions(self, obj):
        return self._google_place(obj).get('author_attributions') or []

    @staticmethod
    def _google_place(obj):
        return getattr(obj, '_google_place_data', {}) or {}

    def get_listing_tier(self, obj):
        if obj.is_featured or getattr(obj, '_has_featured_link', False):
            return 'sponsored'
        if getattr(obj, '_has_recognized_link', False):
            return 'recognized'
        return 'standard'
