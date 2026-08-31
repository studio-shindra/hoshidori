from rest_framework import serializers

from theaters.models import Theater
from .models import Shop, TheaterShop


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
        if getattr(obj, '_has_listed_link', False):
            return 'listed'
        return 'standard'


class ShopOwnerSerializer(serializers.ModelSerializer):
    application_status = serializers.SerializerMethodField()
    theaters = serializers.SerializerMethodField()
    theater_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        required=False,
        queryset=Theater.objects.filter(is_active=True, is_approved=True),
    )

    class Meta:
        model = Shop
        fields = [
            'id', 'name', 'slug', 'category', 'description', 'address',
            'nearest_station', 'distance_note', 'website_url', 'instagram_url',
            'tabelog_url', 'google_map_url', 'google_place_id', 'phone_number',
            'opening_hours_text', 'benefit_text', 'image_url',
            'theaters', 'theater_ids',
            'is_active', 'is_featured', 'application_status', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'slug', 'is_active', 'is_featured', 'application_status',
            'created_at', 'updated_at',
        ]

    def get_application_status(self, obj):
        if not obj.is_active:
            return 'pending'
        if obj.is_featured:
            return 'recommended'
        return 'listed'

    def get_theaters(self, obj):
        return [
            {'id': link.theater_id, 'name': link.theater.name, 'slug': link.theater.slug}
            for link in obj.theater_shops.select_related('theater').all()
        ]

    def update(self, instance, validated_data):
        theaters = validated_data.pop('theater_ids', None)
        instance = super().update(instance, validated_data)
        if theaters is not None:
            instance.theater_shops.exclude(theater__in=theaters).delete()
            for theater in theaters:
                TheaterShop.objects.get_or_create(theater=theater, shop=instance)
        return instance


class ShopApplicationSerializer(serializers.ModelSerializer):
    theater_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        required=False,
        queryset=Theater.objects.filter(is_active=True, is_approved=True),
    )

    class Meta:
        model = Shop
        fields = [
            'name', 'category', 'description', 'address', 'nearest_station',
            'website_url', 'instagram_url', 'google_map_url', 'google_place_id',
            'phone_number', 'opening_hours_text', 'benefit_text',
            'theater_ids',
        ]
        extra_kwargs = {
            'address': {'required': True, 'allow_blank': False},
        }

    def validate(self, attrs):
        request = self.context['request']
        if Shop.objects.filter(owner=request.user).exists():
            raise serializers.ValidationError('このアカウントでは既に店舗を申請しています。')
        place_id = attrs.get('google_place_id', '')
        if place_id and Shop.objects.filter(google_place_id=place_id).exists():
            raise serializers.ValidationError('この店舗は既に登録されています。')
        return attrs

    def create(self, validated_data):
        from uuid import uuid4

        from django.utils.text import slugify

        request = self.context['request']
        theaters = validated_data.pop('theater_ids', [])
        base_slug = slugify(validated_data['name'], allow_unicode=False) or 'shop'
        slug = base_slug
        while Shop.objects.filter(slug=slug).exists():
            slug = f'{base_slug}-{uuid4().hex[:8]}'
        shop = Shop.objects.create(
            **validated_data,
            slug=slug,
            owner=request.user,
            is_active=False,
            is_featured=False,
        )
        TheaterShop.objects.bulk_create([
            TheaterShop(theater=theater, shop=shop)
            for theater in theaters
        ])
        if request.user.role != 'admin':
            request.user.role = 'shop'
            request.user.save(update_fields=['role'])
        return shop
