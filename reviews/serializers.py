from rest_framework import serializers

from .models import Review, ViewingLog


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    performance_str = serializers.StringRelatedField(source='performance', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'performance', 'performance_str',
            'title', 'body', 'rating_overall', 'is_spoiler',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class ViewingLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    performance_str = serializers.StringRelatedField(source='performance', read_only=True)

    class Meta:
        model = ViewingLog
        fields = [
            'id', 'user', 'performance', 'performance_str',
            'watched_on', 'memo', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
