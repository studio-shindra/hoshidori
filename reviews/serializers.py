from rest_framework import serializers
from django.utils import timezone

from config.content_moderation import find_objectionable_phrase
from .models import Like, Review, ReviewReport, UserBlock, ViewingLog, ViewingLogImage


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    user_display_name = serializers.SerializerMethodField()
    user_avatar_url = serializers.SerializerMethodField()
    performance_str = serializers.StringRelatedField(source='performance', read_only=True)
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    after_shop = serializers.SerializerMethodField()
    after_shop_name = serializers.SerializerMethodField()
    after_shop_slug = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'user_id', 'user_display_name', 'user_avatar_url',
            'performance', 'performance_str',
            'title', 'body', 'rating_overall', 'is_spoiler',
            'after_shop', 'after_shop_name', 'after_shop_slug',
            'like_count', 'is_liked',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'user_id', 'created_at', 'updated_at']

    def validate_body(self, value):
        if find_objectionable_phrase(value):
            raise serializers.ValidationError(
                '他の利用者を傷つける可能性のある表現が含まれています。表現を変えてください。'
            )
        return value

    def get_user_display_name(self, obj):
        return obj.user.display_name or obj.user.username

    def get_user_avatar_url(self, obj):
        return obj.user.avatar_url or None

    def get_like_count(self, obj):
        if hasattr(obj, '_like_count'):
            return obj._like_count
        return obj.likes.count()

    def validate_rating_overall(self, value):
        if value is not None and value not in (3, 4, 5):
            raise serializers.ValidationError('評価は 3, 4, 5 のいずれかです。')
        return value

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        if hasattr(obj, '_liked_by_user'):
            return obj._liked_by_user
        return obj.likes.filter(user=request.user).exists()

    def get_after_shop(self, obj):
        return getattr(obj, '_after_shop_id', None)

    def get_after_shop_name(self, obj):
        return getattr(obj, '_after_shop_name', None)

    def get_after_shop_slug(self, obj):
        return getattr(obj, '_after_shop_slug', None)


class LatestReviewSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    user_display_name = serializers.SerializerMethodField()
    user_avatar_url = serializers.SerializerMethodField()
    work_title = serializers.CharField(source='performance.work.title', read_only=True)
    work_slug = serializers.CharField(source='performance.work.slug', read_only=True)
    theater_name = serializers.CharField(source='performance.theater.name', read_only=True)
    after_shop_name = serializers.SerializerMethodField()
    after_shop_slug = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id', 'user_id', 'user_display_name', 'user_avatar_url',
            'work_title', 'work_slug', 'theater_name',
            'after_shop_name', 'after_shop_slug',
            'title', 'body', 'rating_overall',
            'created_at',
        ]

    def get_user_display_name(self, obj):
        return obj.user.display_name or obj.user.username

    def get_user_avatar_url(self, obj):
        return obj.user.avatar_url or None

    def get_after_shop_name(self, obj):
        return getattr(obj, '_after_shop_name', None)

    def get_after_shop_slug(self, obj):
        return getattr(obj, '_after_shop_slug', None)


class ReviewReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewReport
        fields = ['id', 'review', 'reason', 'details', 'status', 'created_at']
        read_only_fields = ['id', 'review', 'status', 'created_at']


class UserBlockSerializer(serializers.ModelSerializer):
    blocked_user_id = serializers.IntegerField(source='blocked_id', read_only=True)
    blocked_display_name = serializers.SerializerMethodField()
    blocked_avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = UserBlock
        fields = [
            'id', 'blocked_user_id', 'blocked_display_name', 'blocked_avatar_url', 'created_at',
        ]
        read_only_fields = fields

    def get_blocked_display_name(self, obj):
        return obj.blocked.display_name or obj.blocked.username

    def get_blocked_avatar_url(self, obj):
        return obj.blocked.avatar_url or None


class ViewingLogImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewingLogImage
        fields = ['id', 'image_url', 'image_public_id', 'image_width', 'image_height', 'image_format', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']


class ViewingLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    work_title = serializers.CharField(source='performance.work.title', read_only=True)
    work_slug = serializers.CharField(source='performance.work.slug', read_only=True)
    theater_name = serializers.CharField(source='performance.theater.name', read_only=True)
    theater_area = serializers.CharField(source='performance.theater.area_name', read_only=True)
    after_shop_name = serializers.CharField(source='after_shop.name', read_only=True)
    after_shop_slug = serializers.CharField(source='after_shop.slug', read_only=True)
    rating = serializers.SerializerMethodField()
    images = ViewingLogImageSerializer(many=True, read_only=True)

    class Meta:
        model = ViewingLog
        fields = [
            'id', 'user', 'performance',
            'work_title', 'work_slug', 'theater_name', 'theater_area',
            'status', 'watched_on', 'watched_time', 'memo',
            'after_shop', 'after_shop_name', 'after_shop_slug',
            'rating', 'images', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_rating(self, obj):
        if hasattr(obj, '_rating'):
            return obj._rating
        return Review.objects.filter(
            user=obj.user, performance=obj.performance,
        ).order_by('-created_at').values_list('rating_overall', flat=True).first()

    def validate(self, data):
        # PATCH時は既存インスタンスの値をフォールバック
        instance = self.instance
        log_status = data.get('status', getattr(instance, 'status', 'watched'))
        watched_on = data.get('watched_on', getattr(instance, 'watched_on', None))

        if log_status == 'watched' and not watched_on:
            raise serializers.ValidationError(
                {'watched_on': 'status が watched の場合、watched_on は必須です。'}
            )
        if log_status == 'watched' and watched_on and watched_on > timezone.localdate():
            raise serializers.ValidationError(
                {'watched_on': '観劇日は今日以前の日付を選んでください。'}
            )
        return data


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'review', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
