from rest_framework import serializers

from .models import PerformanceCast, Performance, Person, Work, WorkEditProposal


class WorkSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    theater_name = serializers.SerializerMethodField()
    start_date = serializers.SerializerMethodField()

    class Meta:
        model = Work
        fields = [
            'id', 'title', 'slug', 'description',
            'created_by', 'is_approved',
            'theater_name', 'start_date',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'is_approved', 'created_at', 'updated_at']
        extra_kwargs = {'slug': {'required': False}}

    def _get_first_performance(self, obj):
        """prefetchデータから最初のパフォーマンスを取得（クエリ発行なし）"""
        perfs = getattr(obj, '_prefetched_performances', None)
        if perfs is not None:
            return perfs[0] if perfs else None
        return obj.performances.select_related('theater').first()

    def get_theater_name(self, obj):
        perf = self._get_first_performance(obj)
        if perf and perf.theater:
            return perf.theater.name
        return None

    def get_start_date(self, obj):
        perf = self._get_first_performance(obj)
        if perf and perf.start_date:
            return str(perf.start_date)
        return None

class PersonSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    work_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Person
        fields = [
            'id', 'name', 'slug', 'phonetic', 'profile_text', 'sns_url',
            'work_count',
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


class WorkEditProposalSerializer(serializers.ModelSerializer):
    proposed_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = WorkEditProposal
        fields = [
            'id', 'work', 'performance', 'proposed_by', 'changes',
            'status', 'created_at', 'reviewed_at',
        ]
        read_only_fields = fields
