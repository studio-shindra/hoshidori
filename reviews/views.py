from django.db.models import Count, Exists, OuterRef, Subquery
from django.db.models.functions import ExtractYear
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from accounts.permissions import IsOwnerOrReadOnly
from .models import Like, Review, ReviewReport, UserBlock, ViewingLog, ViewingLogImage
from .serializers import (
    LatestReviewSerializer, ReviewReportSerializer, ReviewSerializer,
    UserBlockSerializer, ViewingLogImageSerializer, ViewingLogSerializer,
)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        matching_log = ViewingLog.objects.filter(
            user=OuterRef('user'), performance=OuterRef('performance'),
        )
        qs = Review.objects.select_related(
            'user', 'performance__work', 'performance__theater',
        ).annotate(
            _like_count=Count('likes'),
            _after_shop_id=Subquery(matching_log.values('after_shop_id')[:1]),
            _after_shop_name=Subquery(matching_log.values('after_shop__name')[:1]),
            _after_shop_slug=Subquery(matching_log.values('after_shop__slug')[:1]),
        ).order_by('-created_at')

        if self.request.user.is_authenticated:
            qs = qs.annotate(
                _liked_by_user=Exists(
                    Like.objects.filter(review=OuterRef('pk'), user=self.request.user)
                )
            )
            qs = qs.exclude(
                user_id__in=UserBlock.objects.filter(
                    blocker=self.request.user,
                ).values('blocked_id')
            )
        work = self.request.query_params.get('work')
        if work:
            qs = qs.filter(performance__work_id=work)
        return qs

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def latest(self, request):
        matching_log = ViewingLog.objects.filter(
            user=OuterRef('user'), performance=OuterRef('performance'),
        )
        qs = Review.objects.select_related(
            'user', 'performance__work', 'performance__theater',
        ).annotate(
            _after_shop_name=Subquery(matching_log.values('after_shop__name')[:1]),
            _after_shop_slug=Subquery(matching_log.values('after_shop__slug')[:1]),
        ).filter(body__gt='').order_by('-created_at')
        if request.user.is_authenticated:
            qs = qs.exclude(
                user_id__in=UserBlock.objects.filter(
                    blocker=request.user,
                ).values('blocked_id')
            )
        qs = qs[:10]
        serializer = LatestReviewSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    def get_permissions(self):
        if self.action in ('create', 'like'):
            return [IsAuthenticated()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post', 'delete'], url_path='like')
    def like(self, request, pk=None):
        review = self.get_object()
        if request.method == 'POST':
            _, created = Like.objects.get_or_create(user=request.user, review=review)
            if created:
                return Response({'detail': 'いいねしました。'}, status=status.HTTP_201_CREATED)
            return Response({'detail': '既にいいね済みです。'}, status=status.HTTP_200_OK)
        else:
            deleted, _ = Like.objects.filter(user=request.user, review=review).delete()
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'detail': 'いいねしていません。'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def report(self, request, pk=None):
        review = self.get_object()
        if review.user_id == request.user.id:
            return Response({'detail': '自分の投稿は通報できません。'}, status=400)
        serializer = ReviewReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report, created = ReviewReport.objects.update_or_create(
            reporter=request.user,
            review=review,
            defaults={
                'reason': serializer.validated_data['reason'],
                'details': serializer.validated_data.get('details', ''),
                'status': 'pending',
            },
        )
        return Response(
            ReviewReportSerializer(report).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=True, methods=['post'], url_path='block-user', permission_classes=[IsAuthenticated])
    def block_user(self, request, pk=None):
        review = self.get_object()
        if review.user_id == request.user.id:
            return Response({'detail': '自分自身はブロックできません。'}, status=400)
        block, created = UserBlock.objects.get_or_create(
            blocker=request.user, blocked=review.user,
        )
        return Response(
            UserBlockSerializer(block).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class UserBlockViewSet(mixins.ListModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    serializer_class = UserBlockSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserBlock.objects.filter(blocker=self.request.user).select_related('blocked')


class ViewingLogViewSet(ModelViewSet):
    serializer_class = ViewingLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = ViewingLog.objects.filter(
            user=self.request.user,
        ).select_related(
            'performance__work', 'performance__theater', 'after_shop',
        ).prefetch_related(
            'images',
        ).annotate(
            _rating=Subquery(
                Review.objects.filter(
                    user=OuterRef('user'),
                    performance=OuterRef('performance'),
                ).order_by('-created_at').values('rating_overall')[:1]
            ),
        )
        status_filter = self.request.query_params.get('status')
        if status_filter in ('planned', 'watched'):
            qs = qs.filter(status=status_filter)
        year = self.request.query_params.get('year')
        month = self.request.query_params.get('month')
        if year and year.isdigit():
            qs = qs.filter(watched_on__year=int(year))
        if month and month.isdigit() and 1 <= int(month) <= 12:
            qs = qs.filter(watched_on__month=int(month))
        scope = self.request.query_params.get('scope')
        if scope == 'upcoming':
            qs = qs.filter(status='planned', watched_on__gte=timezone.localdate()).order_by(
                'watched_on', 'watched_time', 'created_at',
            )
        elif scope == 'recent':
            qs = qs.filter(status='watched').order_by(
                '-watched_on', '-watched_time', '-created_at',
            )
        return qs

    @action(detail=False, methods=['get'], url_path='calendar')
    def calendar(self, request):
        today = timezone.localdate()
        try:
            year = int(request.query_params.get('year', today.year))
            month = int(request.query_params.get('month', today.month))
        except (TypeError, ValueError):
            return Response({'detail': 'year と month を確認してください。'}, status=400)
        if not 1 <= month <= 12:
            return Response({'detail': 'month は1〜12で指定してください。'}, status=400)
        qs = self.get_queryset().filter(
            watched_on__year=year,
            watched_on__month=month,
        ).order_by('watched_on', 'watched_time', 'created_at')
        serializer = self.get_serializer(qs, many=True)
        return Response({'year': year, 'month': month, 'results': serializer.data})

    @action(detail=False, methods=['get'], url_path='archive')
    def archive(self, request):
        today = timezone.localdate()
        try:
            year = int(request.query_params.get('year', today.year))
        except (TypeError, ValueError):
            return Response({'detail': 'year を確認してください。'}, status=400)
        status_filter = request.query_params.get('status', 'watched')
        if status_filter not in ('planned', 'watched'):
            return Response({'detail': 'status を確認してください。'}, status=400)
        qs = self.get_queryset().filter(
            status=status_filter,
            watched_on__year=year,
        )
        if status_filter == 'planned':
            qs = qs.order_by('watched_on', 'watched_time', 'created_at')
        else:
            qs = qs.order_by('-watched_on', '-watched_time', '-created_at')
        serializer = self.get_serializer(qs, many=True)
        return Response({
            'year': year,
            'status': status_filter,
            'count': qs.count(),
            'results': serializer.data,
        })

    @action(detail=False, methods=['get'], url_path='archive-meta')
    def archive_meta(self, request):
        rows = ViewingLog.objects.filter(
            user=request.user,
            watched_on__isnull=False,
        ).annotate(
            year=ExtractYear('watched_on'),
        ).values('year', 'status').annotate(
            count=Count('id'),
        ).order_by('-year')
        years = {}
        for row in rows:
            year = int(row['year'])
            years.setdefault(year, {'year': year, 'planned': 0, 'watched': 0})
            years[year][row['status']] = row['count']
        return Response({'years': list(years.values())})

    def create(self, request, *args, **kwargs):
        performance_id = request.data.get('performance')
        existing = ViewingLog.objects.filter(
            user=request.user, performance_id=performance_id,
        ).first()

        if existing:
            serializer = self.get_serializer(existing, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='images')
    def add_image(self, request, pk=None):
        viewing_log = self.get_object()
        serializer = ViewingLogImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(viewing_log=viewing_log)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='images/(?P<image_id>[0-9]+)')
    def delete_image(self, request, pk=None, image_id=None):
        viewing_log = self.get_object()
        image = ViewingLogImage.objects.filter(viewing_log=viewing_log, id=image_id).first()
        if not image:
            return Response(status=status.HTTP_404_NOT_FOUND)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
