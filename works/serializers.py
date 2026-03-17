from rest_framework import serializers

from .models import PerformanceCast, Performance, Person, PosterSubmission, Work


class WorkSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    selected_poster_image_url = serializers.SerializerMethodField()
    selected_poster_user_display_name = serializers.SerializerMethodField()
    selected_poster_user_avatar_url = serializers.SerializerMethodField()
    theater_name = serializers.SerializerMethodField()
    start_date = serializers.SerializerMethodField()

    class Meta:
        model = Work
        fields = [
            'id', 'title', 'slug', 'description',
            'created_by', 'is_approved',
            'selected_poster_image_url', 'selected_poster_user_display_name', 'selected_poster_user_avatar_url',
            'theater_name', 'start_date',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'is_approved', 'created_at', 'updated_at']
        extra_kwargs = {'slug': {'required': False}}

    def _get_selected_poster(self, obj):
        """prefetchデータから選択済みポスターを取得（クエリ発行なし）"""
        posters = getattr(obj, '_prefetched_selected_posters', None)
        if posters is not None:
            return posters[0] if posters else None
        # fallback: prefetchなしの場合（detail等）
        return obj.poster_submissions.filter(is_selected=True).select_related('user').first()

    def _get_first_performance(self, obj):
        """prefetchデータから最初のパフォーマンスを取得（クエリ発行なし）"""
        perfs = getattr(obj, '_prefetched_performances', None)
        if perfs is not None:
            return perfs[0] if perfs else None
        return obj.performances.select_related('theater').first()

    def get_selected_poster_image_url(self, obj):
        poster = self._get_selected_poster(obj)
        if poster:
            if poster.image_url:
                return poster.image_url
            if poster.image:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(poster.image.url)
                return poster.image.url
        return None

    def get_theater_name(self, obj):
        perf = self._get_first_performance(obj)
        if perf and perf.theater:
            return perf.theater.name
        return None

    def get_start_date(self, obj):
        perf = self._get_first_performance(obj)
        if perf:
            return str(perf.start_date)
        return None

    def get_selected_poster_user_display_name(self, obj):
        poster = self._get_selected_poster(obj)
        if poster:
            return poster.user.display_name or poster.user.username
        return None

    def get_selected_poster_user_avatar_url(self, obj):
        poster = self._get_selected_poster(obj)
        if poster:
            return poster.user.avatar_url or None
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
    theater_slug = serializers.CharField(source='theater.slug', read_only=True)
    casts = PerformanceCastSerializer(many=True, read_only=True)

    class Meta:
        model = Performance
        fields = [
            'id', 'work', 'work_title', 'theater', 'theater_name', 'theater_slug',
            'company_name', 'start_date', 'end_date', 'note',
            'created_by', 'is_approved', 'casts', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'is_approved', 'created_at', 'updated_at']


class PosterSubmissionSerializer(serializers.ModelSerializer):
    user_display_name = serializers.SerializerMethodField()
    user_avatar_url = serializers.SerializerMethodField()
    work_title = serializers.CharField(source='work.title', read_only=True)

    class Meta:
        model = PosterSubmission
        fields = [
            'id', 'work', 'work_title', 'user', 'user_display_name', 'user_avatar_url',
            'image', 'image_url', 'image_public_id',
            'image_width', 'image_height', 'image_format',
            'caption', 'is_selected', 'created_at',
        ]
        read_only_fields = ['id', 'work', 'user', 'is_selected', 'created_at']

    def get_user_display_name(self, obj):
        return obj.user.display_name or obj.user.username

    def get_user_avatar_url(self, obj):
        return obj.user.avatar_url or None

    def validate_image_url(self, value):
        if value and 'res.cloudinary.com' not in value:
            raise serializers.ValidationError('Cloudinary以外の画像URLは使用できません')
        return value

    def validate(self, data):
        # PATCH時は既存データをフォールバック
        instance = self.instance
        has_image = data.get('image') or (instance and instance.image)
        has_url = data.get('image_url') or (instance and instance.image_url)
        if not has_image and not has_url:
            raise serializers.ValidationError('image または image_url が必要です')
        image_url = data.get('image_url')
        if image_url and not data.get('image_public_id', getattr(instance, 'image_public_id', '')):
            raise serializers.ValidationError('image_public_id は必須です')
        return data
