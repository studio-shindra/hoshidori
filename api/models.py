from django.db import models
from django.contrib.auth import get_user_model
from cloudinary.models import CloudinaryField
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone 

User = get_user_model()


class UserProfile(models.Model):
    """
    ユーザープロフィール（デフォルト User モデルの拡張）
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_image = CloudinaryField('profile image', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.user.username} Profile'


class WorkStatus(models.TextChoices):
    DRAFT = 'DRAFT', '仮作品（作成者のみ）'
    PENDING = 'PENDING', '審査中'
    APPROVED = 'APPROVED', '公開'


class Tag(models.Model):
    """
    タグモデル（作品とログで共用）
    """
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Theater(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    area = models.CharField(
        max_length=100,
        blank=True,
        help_text='メインのエリア（例：東京／名古屋／大阪）'
    )
    address = models.CharField(max_length=255, blank=True)
    image_url = models.URLField(blank=True)

    # ★ 複数エリアタグ用の配列フィールド
    area_tags = ArrayField(
        base_field=models.CharField(max_length=100),
        blank=True,
        default=list,
        help_text='エリアタグ（例：["新宿", "小劇場"]）'
    )

    def __str__(self) -> str:
        return f'{self.name} ({self.area})' if self.area else self.name


class Actor(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Troupe(models.Model):
    """
    劇団 / 制作 / プロデュース単位。
    - ここに画像許諾フラグを持たせる
    """
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    official_site = models.URLField(blank=True)
    image_allowed = models.BooleanField(
        default=False,
        help_text="ポスター等の画像をHOSHIDORI内で表示してよいか（許諾○/×）"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Work(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    is_quick_created = models.BooleanField(default=False)
    
    troupe = models.ForeignKey(
        Troupe,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="works",
        help_text="劇団 / 制作"
    )
    
    description = models.TextField(blank=True)
    main_image = CloudinaryField('main image', blank=True, null=True)

    main_theater = models.ForeignKey(
        Theater, null=True, blank=True,
        on_delete=models.SET_NULL
    )

    # 作品の性質タグ（ジャンルなど）
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='works',
        help_text='作品タグ（会話劇、一人芝居、SF など）'
    )

    actors = models.ManyToManyField(
        Actor, blank=True,
        related_name='works'
    )

    status = models.CharField(
        max_length=20,
        choices=WorkStatus.choices,
        default=WorkStatus.APPROVED,
        help_text='DRAFT: 作成者のみ閲覧可 / PENDING: 要確認 / APPROVED: 公開'
    )
    admin_note = models.TextField(blank=True)

    # Cloudinary URL を直接持ちたい場合に利用（不要なら削除可）
    main_image_url = models.URLField(blank=True)

    # 公式URL・SNS
    official_site = models.URLField(blank=True, help_text='公式サイト')
    official_x = models.URLField(blank=True, help_text='公式X（Twitter）')
    official_instagram = models.URLField(blank=True, help_text='公式Instagram')
    official_tiktok = models.URLField(blank=True, help_text='公式TikTok')

    created_by = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='created_works'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title


class Run(models.Model):
    work = models.ForeignKey(
        Work, on_delete=models.CASCADE, related_name='runs'
    )
    label = models.CharField(
        max_length=200,
        help_text='本公演／地方公演などのラベル'
    )
    area = models.CharField(
        max_length=100,
        blank=True,
        help_text='エリア（例：東京／名古屋／大阪）'
    )
    theater = models.ForeignKey(
        Theater, null=True, blank=True,
        on_delete=models.SET_NULL
    )

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.work.title} - {self.label}'


class ViewingLog(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='viewing_logs'
    )
    work = models.ForeignKey(
        Work, on_delete=models.CASCADE,
        related_name='logs'
    )
    run = models.ForeignKey(
        Run, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='logs',
        help_text='どの公演ブロック（東京公演/大阪公演等）で観たか（任意）'
    )

    watched_at = models.DateTimeField(help_text='観劇日時')
    seat = models.CharField(max_length=100, blank=True)
    memo = models.TextField(blank=True)
    rating = models.DecimalField(
        max_digits=3, decimal_places=1,
        null=True, blank=True,
        help_text='1.0〜5.0の評価（小数点第一位まで）'
    )

    # ログ固有のタグ（感情・状況など）
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='logs',
        help_text='ログ用タグ（泣いた、初見、千秋楽など）'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-watched_at', '-created_at']

    def __str__(self) -> str:
        return f'{self.user} - {self.work} ({self.watched_at.date()})'


class WorkRating(models.Model):
    """ログを保存しないゲスト等からの評価専用テーブル"""
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        who = self.user.username if self.user else 'guest'
        return f'{who} → {self.work} : {self.rating}'