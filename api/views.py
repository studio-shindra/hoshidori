from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import viewsets, permissions, decorators, response, filters, status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import Work, ViewingLog, Theater, Actor, Tag, UserProfile
from .models import Troupe
from .rating_utils import add_rating_entry, calculate_avg_rating
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from .serializers import (
    WorkListSerializer,
    WorkDetailSerializer,
    WorkCreateOrGetSerializer,
    RunSerializer,
    ViewingLogSerializer,
    RegisterSerializer,
    TheaterSerializer,
    ActorSerializer,
    TroupeSerializer,
    ContactSerializer,
    UserSerializer,
)

User = get_user_model()



class WorkViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'main_theater']
    # ForeignKey（troupe）は search_fields に含めない（SearchFilter は ForeignKey をサポートしない）
    # 代わりに troupe__name で検索可能にする
    search_fields = ['title', 'troupe__name', 'tags__name', 'actors__name']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
    serializer_class = WorkDetailSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = Work.objects.select_related('main_theater').prefetch_related(
            'tags', 'runs__theater'
        )
        user = self.request.user

        # 一覧検索は公開作品のみ（クイック作成を除外）
        if self.action in ['list']:
            return qs.filter(
                status='APPROVED',
                is_quick_created=False,
            )

        # それ以外（詳細など）はログイン状態に応じて公開＋自分の下書き・クイック作品を許可
        from django.db.models import Q
        if user.is_authenticated:
            return qs.filter(
                Q(is_quick_created=False, status__in=['APPROVED', 'PENDING']) |
                Q(created_by=user)
            )

        return qs.filter(is_quick_created=False, status__in=['APPROVED', 'PENDING'])

    def get_serializer_class(self):  # type: ignore[override]
        if self.action in ['list']:
            return WorkListSerializer
        return WorkDetailSerializer

    def get_permissions(self):
        # 一覧・詳細・スケジュール・本日の時間候補・評価付与は公開、それ以外（作成・更新・削除）は要ログイン
        if self.action in ['list', 'retrieve', 'schedule', 'today_times', 'rate']:
            return [AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, status='PENDING')

    @decorators.action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        work = self.get_object()
        runs = work.runs.all().prefetch_related('theater')
        ser = RunSerializer(runs, many=True)
        return response.Response({
            'work_id': work.id,
            'title': work.title,
            'runs': ser.data,
        })

    @decorators.action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def create_or_get(self, request):
        """
        POST /api/works/create_or_get/
        Workを作成または既存取得するエンドポイント
        """
        serializer = WorkCreateOrGetSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        work = serializer.save()
        # 作成済みWorkを詳細情報で返却
        detail_ser = WorkDetailSerializer(work)
        return response.Response(detail_ser.data, status=status.HTTP_201_CREATED)

    @decorators.action(detail=True, methods=['get'])
    def today_times(self, request, pk=None):
        """
        GET /api/works/{id}/today_times/
        今日の公演時間候補を返す
        """
        from django.utils import timezone
        work = self.get_object()
        today = timezone.localdate()
        logs = ViewingLog.objects.filter(
            work=work,
            watched_at__date=today
        ).values_list('watched_at', flat=True)
        # 時間部分を抽出してユニーク化
        times = sorted(set(dt.strftime('%H:%M') for dt in logs))
        return response.Response({'times': times})

    @decorators.action(detail=True, methods=['post'], permission_classes=[AllowAny], authentication_classes=[])
    def rate(self, request, pk=None):
        """ゲストでも利用可能な作品への評価付与エンドポイント"""
        work = self.get_object()
        rating_val = request.data.get('rating')

        try:
            rating = float(rating_val)
        except (TypeError, ValueError):
            return response.Response({'detail': 'rating は数値で指定してください'}, status=status.HTTP_400_BAD_REQUEST)

        if rating < 1 or rating > 5:
            return response.Response({'detail': 'rating は1.0〜5.0の範囲で指定してください'}, status=status.HTTP_400_BAD_REQUEST)

        avg = add_rating_entry(work, rating, request.user if request.user.is_authenticated else None)
        return response.Response({'avg_rating': avg}, status=status.HTTP_201_CREATED)


class ViewingLogViewSet(viewsets.ModelViewSet):
    serializer_class = ViewingLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['work', 'run', 'rating']
    ordering_fields = ['watched_at', 'created_at']
    ordering = ['-watched_at', '-created_at']

    def get_queryset(self):
        # 自分のログだけ
        return ViewingLog.objects.filter(user=self.request.user).select_related('work', 'run')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        # rating ありの場合は平均計算を更新しておく（結果はレスポンスには含めない）
        if serializer.instance.rating:
            calculate_avg_rating(serializer.instance.work)


class TheaterViewSet(viewsets.ModelViewSet):
    """劇場一覧・詳細・作成"""
    queryset = Theater.objects.all()
    serializer_class = TheaterSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'area', 'area_tags']
    ordering = ['name']


class ActorViewSet(viewsets.ModelViewSet):
    """俳優一覧・作成"""
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering = ['name']


class TroupeViewSet(viewsets.ModelViewSet):
    """劇団一覧・作成"""
    queryset = Troupe.objects.all()
    serializer_class = TroupeSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'slug']
    ordering = ['name']


User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    username / password / (email) でゆる登録
    """
    ser = RegisterSerializer(data=request.data)
    if ser.is_valid():
        ser.save()
        return Response(ser.data, status=status.HTTP_201_CREATED)
    return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactView(APIView):
    permission_classes = [permissions.AllowAny]  # 誰でも送れる問い合わせフォーム想定

    def post(self, request, *args, **kwargs):
        serializer = ContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        subject = f"[HOSHIDORI] お問い合わせ: {data['name']}"
        body = (
            f"お名前: {data['name']}\n"
            f"メール: {data['email']}\n\n"
            f"本文:\n{data['message']}"
        )

        send_mail(
            subject=subject,
            message=body,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            recipient_list=[getattr(settings, "CONTACT_EMAIL", settings.DEFAULT_FROM_EMAIL)],
        )

        return Response({"detail": "ok"}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def tags_list(request):
    """
    既存タグ一覧を取得
    Multiselect のオプションとして使用
    """
    tags = Tag.objects.all().values('id', 'name').order_by('name')
    return Response([{'value': tag['id'], 'label': tag['name']} for tag in tags])


class UserView(APIView):
    """
    ユーザープロフィール管理
    GET: ユーザー情報を取得
    PATCH: ユーザー情報（プロフィール画像含む）を更新
    DELETE: アカウント削除
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        """GET /api/auth/user/ - ユーザープロフィール取得"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        """PATCH /api/auth/user/ - ユーザープロフィール更新"""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # プロフィール画像を処理
            if 'profile_image' in request.FILES:
                profile, _ = UserProfile.objects.get_or_create(user=request.user)
                profile.profile_image = request.FILES['profile_image']
                profile.save()

            # 更新後のデータを返す
            return Response(UserSerializer(request.user).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """DELETE /api/auth/user/ - アカウント削除"""
        user = request.user
        user.delete()
        return Response({'detail': 'Account deleted'}, status=status.HTTP_204_NO_CONTENT)