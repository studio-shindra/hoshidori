# api/serializers.py（一部）

from taggit.models import Tag
from rest_framework import serializers
from .models import Theater, Actor, Work, Run, ViewingLog
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.db import IntegrityError, transaction


class TheaterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theater
        fields = ['id', 'name', 'slug', 'area', 'address', 'image_url']


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ['id', 'name']


class WorkListSerializer(serializers.ModelSerializer):
    main_theater = TheaterSerializer(read_only=True)
    main_image = serializers.ImageField(read_only=True)
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name',
    )
    avg_rating = serializers.SerializerMethodField()

    def get_avg_rating(self, obj):
        """この作品の全ユーザーの評価平均を計算"""
        from django.db.models import Avg
        result = ViewingLog.objects.filter(work=obj, rating__isnull=False).aggregate(Avg('rating'))
        avg = result.get('rating__avg')
        return round(avg, 1) if avg else None

    class Meta:
        model = Work
        fields = [
            'id',
            'title',
            'slug',
            'troupe',
            'main_theater',
            'status',
            'main_image',
            'tags',
            'avg_rating',
        ]


class RunSerializer(serializers.ModelSerializer):
    theater = TheaterSerializer(read_only=True)

    class Meta:
        model = Run
        fields = [
            'id',
            'label',
            'area',
            'theater',
            'start_date',
            'end_date',
        ]


class WorkDetailSerializer(serializers.ModelSerializer):
    main_theater = TheaterSerializer(read_only=True)
    actors = ActorSerializer(many=True, read_only=True)
    runs = RunSerializer(many=True, read_only=True)
    main_image = serializers.ImageField(read_only=True)
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name',
    )
    avg_rating = serializers.SerializerMethodField()

    def get_avg_rating(self, obj):
        """この作品の全ユーザーの評価平均を計算"""
        from django.db.models import Avg
        result = ViewingLog.objects.filter(work=obj, rating__isnull=False).aggregate(Avg('rating'))
        avg = result.get('rating__avg')
        return round(avg, 1) if avg else None

    class Meta:
        model = Work
        fields = [
            'id',
            'title',
            'slug',
            'troupe',
            'description',
            'main_theater',
            'status',
            'main_image',
            'tags',
            'actors',
            'runs',
            'avg_rating',
        ]


class ViewingLogSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name',
    )

    class Meta:
        model = ViewingLog
        fields = [
            'id',
            'user',
            'work',
            'run',
            'watched_at',
            'seat',
            'memo',
            'rating',
            'tags',
            'created_at',
        ]
        read_only_fields = ['user', 'created_at']


class WorkCreateOrGetSerializer(serializers.Serializer):
    """
    Workを作成または既存取得するAPI用シリアライザ
    """
    title = serializers.CharField(max_length=200)
    troupe = serializers.CharField(max_length=200, required=False, allow_blank=True)
    main_theater_id = serializers.IntegerField(required=False, allow_null=True)
    # 最初のRun情報（任意）
    run_label = serializers.CharField(max_length=200, required=False, allow_blank=True)
    run_area = serializers.CharField(max_length=100, required=False, allow_blank=True)
    run_theater_id = serializers.IntegerField(required=False, allow_null=True)
    run_start_date = serializers.DateField(required=False, allow_null=True)
    run_end_date = serializers.DateField(required=False, allow_null=True)

    def create(self, validated_data):
        user = self.context['request'].user
        title = validated_data['title']
        troupe = validated_data.get('troupe', '')
        main_theater_id = validated_data.get('main_theater_id')

        # slug生成
        base_slug = slugify(title)
        slug = base_slug
        counter = 1

        # Work作成または取得
        work = None
        with transaction.atomic():
            while True:
                try:
                    work = Work.objects.create(
                        title=title,
                        slug=slug,
                        troupe=troupe,
                        main_theater_id=main_theater_id,
                        status='DRAFT',
                        created_by=user,
                    )
                    break
                except IntegrityError:
                    # slug重複の場合、既存を取得
                    existing = Work.objects.filter(slug=slug).first()
                    if existing:
                        work = existing
                        break
                    # 万が一の場合はカウンタを付けて再試行
                    slug = f"{base_slug}-{counter}"
                    counter += 1

        # Run情報があれば作成
        run_label = validated_data.get('run_label')
        if run_label and work:
            Run.objects.get_or_create(
                work=work,
                label=run_label,
                defaults={
                    'area': validated_data.get('run_area', ''),
                    'theater_id': validated_data.get('run_theater_id'),
                    'start_date': validated_data.get('run_start_date'),
                    'end_date': validated_data.get('run_end_date'),
                }
            )

        return work


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user