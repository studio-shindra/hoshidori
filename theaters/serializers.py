from rest_framework import serializers

from .models import Theater


class TheaterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theater
        fields = [
            'id', 'name', 'slug', 'area_name', 'address',
            'nearest_station', 'description', 'website_url',
            'image', 'image_url', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
