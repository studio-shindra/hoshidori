from rest_framework import serializers

from .models import Like, Review, ViewingLog


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_display_name = serializers.SerializerMethodField()
    user_avatar_url = serializers.SerializerMethodField()
    performance_str = serializers.StringRelatedField(source='performance', read_only=True)
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'user_display_name', 'user_avatar_url',
            'performance', 'performance_str',
            'title', 'body', 'rating_overall', 'is_spoiler',
            'like_count', 'is_liked',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

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


class LatestReviewSerializer(serializers.ModelSerializer):
    user_display_name = serializers.SerializerMethodField()
    user_avatar_url = serializers.SerializerMethodField()
    work_title = serializers.CharField(source='performance.work.title', read_only=True)
    work_slug = serializers.CharField(source='performance.work.slug', read_only=True)
    poster_url = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id', 'user_display_name', 'user_avatar_url',
            'work_title', 'work_slug', 'poster_url',
            'title', 'body', 'rating_overall',
            'created_at',
        ]

    def get_user_display_name(self, obj):
        return obj.user.display_name or obj.user.username

    def get_user_avatar_url(self, obj):
        return obj.user.avatar_url or None

    def get_poster_url(self, obj):
        posters = getattr(obj.performance.work, '_prefetched_selected_posters', None)
        if posters is not None:
            poster = posters[0] if posters else None
        else:
            poster = obj.performance.work.poster_submissions.filter(is_selected=True).first()
        if not poster:
            return None
        if poster.image_url:
            return poster.image_url
        if poster.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(poster.image.url)
            return poster.image.url
        return None


class ViewingLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    work_title = serializers.CharField(source='performance.work.title', read_only=True)
    work_slug = serializers.CharField(source='performance.work.slug', read_only=True)
    theater_name = serializers.CharField(source='performance.theater.name', read_only=True)
    theater_area = serializers.CharField(source='performance.theater.area_name', read_only=True)
    poster_url = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = ViewingLog
        fields = [
            'id', 'user', 'performance',
            'work_title', 'work_slug', 'theater_name', 'theater_area',
            'poster_url', 'status', 'watched_on', 'watched_time', 'memo',
            'rating', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_poster_url(self, obj):
        posters = getattr(obj.performance.work, '_prefetched_selected_posters', None)
        if posters is not None:
            poster = posters[0] if posters else None
        else:
            poster = obj.performance.work.poster_submissions.filter(is_selected=True).first()
        if not poster:
            return None
        if poster.image_url:
            return poster.image_url
        if poster.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(poster.image.url)
            return poster.image.url
        return None

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
        if log_status == 'planned':
            if 'watched_on' not in data:
                data['watched_on'] = None
            data['watched_time'] = None
        return data


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'review', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
