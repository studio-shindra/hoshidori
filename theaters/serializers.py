from rest_framework import serializers

from .models import Theater


class TheaterSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    def validate(self, attrs):
        name = (attrs.get('name') or getattr(self.instance, 'name', '')).strip()
        address = (attrs.get('address') or getattr(self.instance, 'address', '')).strip()
        if not name:
            raise serializers.ValidationError({'name': '劇場名は必須です。'})

        duplicates = Theater.objects.filter(name__iexact=name)
        if address:
            duplicates = duplicates.filter(address__iexact=address)
        if self.instance:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise serializers.ValidationError({'name': '同じ劇場がすでに登録されています。'})
        return attrs

    class Meta:
        model = Theater
        fields = [
            'id', 'name', 'slug', 'area_name', 'address',
            'nearest_station', 'description', 'website_url',
            'image', 'image_url', 'is_active', 'created_at', 'updated_at',
            'google_place_id', 'source_url', 'prefecture', 'city',
            'created_by', 'is_approved',
        ]
        read_only_fields = ['id', 'created_by', 'is_approved', 'created_at', 'updated_at']
        extra_kwargs = {'slug': {'required': False}}
