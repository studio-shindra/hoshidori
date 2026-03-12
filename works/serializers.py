from rest_framework import serializers

from .models import PerformanceCast, Performance, Person, Work


class WorkSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Work
        fields = [
            'id', 'title', 'slug', 'description',
            'created_by', 'is_approved', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'is_approved', 'created_at', 'updated_at']


class PersonSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Person
        fields = [
            'id', 'name', 'slug', 'phonetic', 'profile_text', 'sns_url',
            'created_by', 'is_approved', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'is_approved', 'created_at', 'updated_at']


class PerformanceCastSerializer(serializers.ModelSerializer):
    person_name = serializers.CharField(source='person.name', read_only=True)

    class Meta:
        model = PerformanceCast
        fields = ['id', 'person', 'person_name', 'role_name']
        read_only_fields = ['id']


class PerformanceSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    work_title = serializers.CharField(source='work.title', read_only=True)
    theater_name = serializers.CharField(source='theater.name', read_only=True)
    casts = PerformanceCastSerializer(many=True, read_only=True)

    class Meta:
        model = Performance
        fields = [
            'id', 'work', 'work_title', 'theater', 'theater_name',
            'company_name', 'start_date', 'end_date', 'note',
            'created_by', 'is_approved', 'casts', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'is_approved', 'created_at', 'updated_at']
