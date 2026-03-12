from rest_framework import serializers

from .models import Like, Review, ViewingLog


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    performance_str = serializers.StringRelatedField(source='performance', read_only=True)
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'performance', 'performance_str',
            'title', 'body', 'rating_overall', 'is_spoiler',
            'like_count', 'is_liked',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_like_count(self, obj):
        if hasattr(obj, '_like_count'):
            return obj._like_count
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        if hasattr(obj, '_liked_by_user'):
            return obj._liked_by_user
        return obj.likes.filter(user=request.user).exists()


class ViewingLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    performance_str = serializers.StringRelatedField(source='performance', read_only=True)

    class Meta:
        model = ViewingLog
        fields = [
            'id', 'user', 'performance', 'performance_str',
            'status', 'watched_on', 'memo', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate(self, data):
        # PATCH時は既存インスタンスの値をフォールバック
        instance = self.instance
        log_status = data.get('status', getattr(instance, 'status', 'watched'))
        watched_on = data.get('watched_on', getattr(instance, 'watched_on', None))

        if log_status == 'watched' and not watched_on:
            raise serializers.ValidationError(
                {'watched_on': 'status が watched の場合、watched_on は必須です。'}
            )
        if log_status == 'planned' and 'watched_on' not in data:
            data['watched_on'] = None
        return data


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'review', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
