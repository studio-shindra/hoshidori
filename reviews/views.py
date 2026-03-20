from django.db.models import Count, Exists, OuterRef, Prefetch, Subquery

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import IsOwnerOrReadOnly
from works.models import PosterSubmission
from .models import Like, Review, ViewingLog, ViewingLogImage
from .serializers import LatestReviewSerializer, ReviewSerializer, ViewingLogImageSerializer, ViewingLogSerializer


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        qs = Review.objects.select_related(
            'user', 'performance__work', 'performance__theater',
        ).annotate(_like_count=Count('likes'))

        if self.request.user.is_authenticated:
            qs = qs.annotate(
                _liked_by_user=Exists(
                    Like.objects.filter(review=OuterRef('pk'), user=self.request.user)
                )
            )
        work = self.request.query_params.get('work')
        if work:
            qs = qs.filter(performance__work_id=work)
        return qs

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def latest(self, request):
        qs = Review.objects.select_related(
            'user', 'performance__work', 'performance__theater',
        ).prefetch_related(
            Prefetch(
                'performance__work__poster_submissions',
                queryset=PosterSubmission.objects.filter(is_selected=True),
                to_attr='_prefetched_selected_posters',
            ),
        ).filter(body__gt='').order_by('-created_at')[:10]
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


class ViewingLogViewSet(ModelViewSet):
    serializer_class = ViewingLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = ViewingLog.objects.filter(
            user=self.request.user,
        ).select_related(
            'performance__work', 'performance__theater',
        ).prefetch_related(
            Prefetch(
                'performance__work__poster_submissions',
                queryset=PosterSubmission.objects.filter(is_selected=True),
                to_attr='_prefetched_selected_posters',
            ),
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
        return qs

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
