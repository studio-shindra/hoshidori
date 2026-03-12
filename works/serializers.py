from rest_framework import serializers

from .models import PerformanceCast, Performance, Person, PosterSubmission, Work


class WorkSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    selected_poster_image_url = serializers.SerializerMethodField()
    selected_poster_user_display_name = serializers.SerializerMethodField()

    class Meta:
        model = Work
        fields = [
            'id', 'title', 'slug', 'description',
            'created_by', 'is_approved',
            'selected_poster_image_url', 'selected_poster_user_display_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'is_approved', 'created_at', 'updated_at']
        extra_kwargs = {'slug': {'required': False}}

    def get_selected_poster_image_url(self, obj):
        poster = getattr(obj, '_selected_poster', None)
        if poster is None:
            poster = obj.poster_submissions.filter(is_selected=True).first()
        if poster and poster.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(poster.image.url)
            return poster.image.url
        return None

    def get_selected_poster_user_display_name(self, obj):
        poster = getattr(obj, '_selected_poster', None)
        if poster is None:
            poster = obj.poster_submissions.filter(is_selected=True).select_related('user').first()
        if poster:
            return poster.user.display_name or poster.user.username
        return None


class PersonSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Person
        fields = [
            'id', 'name', 'slug', 'phonetic', 'profile_text', 'sns_url',
            'created_by', 'is_approved', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'is_approved', 'created_at', 'updated_at']
        extra_kwargs = {'slug': {'required': False}}


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


class PosterSubmissionSerializer(serializers.ModelSerializer):
    user_display_name = serializers.SerializerMethodField()

    class Meta:
        model = PosterSubmission
        fields = ['id', 'work', 'user', 'user_display_name', 'image', 'caption', 'is_selected', 'created_at']
        read_only_fields = ['id', 'user', 'is_selected', 'created_at']

    def get_user_display_name(self, obj):
        return obj.user.display_name or obj.user.username
