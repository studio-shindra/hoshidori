from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import viewsets, permissions, decorators, response, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Work, ViewingLog, Theater, Actor
from .models import Troupe
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
)


class WorkViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'main_theater']
    search_fields = ['title', 'troupe', 'tags__name', 'actors__name']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
    serializer_class = WorkDetailSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        # APPROVED/PENDINGは公開、DRAFTは作成者本人のみ
        qs = Work.objects.select_related('main_theater').prefetch_related(
            'tags', 'runs__theater'
        )
        user = self.request.user
        if user.is_authenticated:
            # ログイン済み: APPROVED/PENDING + 自分のDRAFT
            from django.db.models import Q
            return qs.filter(
                Q(status__in=['APPROVED', 'PENDING']) | Q(status='DRAFT', created_by=user)
            )
        else:
            # 未ログイン: APPROVED/PENDINGのみ
            return qs.filter(status__in=['APPROVED', 'PENDING'])

    def get_serializer_class(self):  # type: ignore[override]
        if self.action in ['list']:
            return WorkListSerializer
        return WorkDetailSerializer

    def get_permissions(self):
        # 一覧・詳細・スケジュールは公開、それ以外（作成・更新・削除）は要ログイン
        if self.action in ['list', 'retrieve', 'schedule']:
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


class TroupeViewSet(viewsets.ModelViewSet):
    """劇団一覧・作成"""
    queryset = Troupe.objects.all()
    serializer_class = TroupeSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'slug']
    ordering = ['name']
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
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