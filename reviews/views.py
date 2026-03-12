from django.db.models import Count, Exists, OuterRef

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import IsOwnerOrReadOnly
from .models import Like, Review, ViewingLog
from .serializers import ReviewSerializer, ViewingLogSerializer


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
        return qs

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
            user=self.request.user
        ).select_related('performance__work', 'performance__theater')
        status_filter = self.request.query_params.get('status')
        if status_filter in ('planned', 'watched'):
            qs = qs.filter(status=status_filter)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
