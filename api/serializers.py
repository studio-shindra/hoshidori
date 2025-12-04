# api/serializers.py（一部）

from rest_framework import serializers
from .models import Theater, Actor, Troupe, Work, Run, ViewingLog, Tag
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.db import IntegrityError, transaction
import uuid


class TheaterSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        """POST時にslugがなければ自動生成"""
        if not validated_data.get('slug'):
            validated_data['slug'] = slugify(validated_data.get('name', ''))
        return super().create(validated_data)

    class Meta:
        model = Theater
        fields = ['id', 'name', 'slug', 'area', 'address', 'image_url']


class ActorSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        """POST時に重複存在すれば既存を返す"""
        actor, created = Actor.objects.get_or_create(**validated_data)
        return actor

    class Meta:
        model = Actor
        fields = ['id', 'name']


class TroupeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Troupe
        fields = ['id', 'name', 'slug', 'official_site', 'image_allowed']


class WorkListSerializer(serializers.ModelSerializer):
    main_theater = TheaterSerializer(read_only=True)
    troupe = TroupeSerializer(read_only=True)
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
            'official_site',
            'official_x',
            'official_instagram',
            'official_tiktok',
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
    troupe = TroupeSerializer(read_only=True)
    actors = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Actor.objects.all(),
        required=False,
    )
    runs = RunSerializer(many=True, read_only=True)
    main_image = serializers.ImageField(required=False, allow_null=True)
    tags = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Tag.objects.all(),
        required=False,
    )
    avg_rating = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    def get_avg_rating(self, obj):
        """この作品の全ユーザーの評価平均を計算"""
        from django.db.models import Avg
        result = ViewingLog.objects.filter(work=obj, rating__isnull=False).aggregate(Avg('rating'))
        avg = result.get('rating__avg')
        return round(avg, 1) if avg else None

    def get_comment_count(self, obj):
        """この作品のコメント（メモ）数を計算"""
        return ViewingLog.objects.filter(work=obj, memo__isnull=False).exclude(memo='').count()

    def to_representation(self, instance):
        """読み取り時は ActorSerializer で詳細を返す"""
        data = super().to_representation(instance)
        data['actors'] = ActorSerializer(instance.actors.all(), many=True).data
        return data

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
            'comment_count',
            'official_site',
            'official_x',
            'official_instagram',
            'official_tiktok',
        ]


class ViewingLogSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        slug_field='name',
    )
    # 書き込み用: フロントから数値IDを受け取る
    work_id = serializers.PrimaryKeyRelatedField(
        queryset=Work.objects.all(),
        source='work',
        write_only=True,
    )
    # 読み取り用: ネストした work オブジェクトを返す
    work = WorkListSerializer(read_only=True)

    class Meta:
        model = ViewingLog
        fields = [
            'id',
            'user',
            'work',
            'work_id',
            'run',
            'watched_at',
            'seat',
            'memo',
            'rating',
            'tags',
            'created_at',
        ]
        read_only_fields = ['user', 'created_at']

    def validate(self, attrs):
        # work 必須チェック（新規作成時のみ）
        if not attrs.get('work') and not self.instance:
            raise serializers.ValidationError({'work': '作品は必須です。'})
        return attrs

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # watched_at → watchedDate にキャメルケース化
        if 'watched_at' in ret:
            ret['watchedDate'] = ret.pop('watched_at')
        return ret


class WorkCreateOrGetSerializer(serializers.Serializer):
    """
    Workを作成または既存取得するAPI用シリアライザ
    """
    title = serializers.CharField(max_length=200)
    troupe = serializers.CharField(max_length=200, required=False, allow_blank=True)
    main_theater_id = serializers.IntegerField(required=False, allow_null=True)
    # 公式URL・SNS
    official_site = serializers.URLField(required=False, allow_blank=True)
    official_x = serializers.URLField(required=False, allow_blank=True)
    official_instagram = serializers.URLField(required=False, allow_blank=True)
    official_tiktok = serializers.URLField(required=False, allow_blank=True)
    # 最初のRun情報（任意）
    run_label = serializers.CharField(max_length=200, required=False, allow_blank=True)
    run_area = serializers.CharField(max_length=100, required=False, allow_blank=True)
    run_theater_id = serializers.IntegerField(required=False, allow_null=True)
    run_start_date = serializers.DateField(required=False, allow_null=True)
    run_end_date = serializers.DateField(required=False, allow_null=True)

    def create(self, validated_data):
        user = self.context['request'].user
        title = validated_data['title']
        troupe_name = validated_data.get('troupe', '')
        main_theater_id = validated_data.get('main_theater_id')
        # 公式URL・SNS
        official_site = validated_data.get('official_site', '')
        official_x = validated_data.get('official_x', '')
        official_instagram = validated_data.get('official_instagram', '')
        official_tiktok = validated_data.get('official_tiktok', '')

        # troupe_name が指定されていれば Troupe を取得または作成
        troupe = None
        if troupe_name:
            troupe, _ = Troupe.objects.get_or_create(
                name=troupe_name,
                defaults={'slug': slugify(troupe_name)}
            )

        # slug生成
        base_slug = slugify(title)
        # slugがから空になる場合のフォールバック（記号だけのタイトル等）
        if not base_slug:
            base_slug = f"work-{user.id}"
        # slug生成：UUIDで完全に一意性を保証
        slug = str(uuid.uuid4())
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
                        official_site=official_site,
                        official_x=official_x,
                        official_instagram=official_instagram,
                        official_tiktok=official_tiktok,
                        status='APPROVED',
                        created_by=user,
                    )
                    break
                except IntegrityError:
                    # slug重複の場合、既存を取得
                    existing = Work.objects.filter(slug=slug).first()
                    if existing:
                        work = existing
                        break
                    # 万が一の場合は別のUUIDで再試行
                    slug = str(uuid.uuid4())
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


# メールフォーム用簡易シリアライザ
class ContactSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    message = serializers.CharField()