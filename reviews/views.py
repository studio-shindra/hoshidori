from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import IsOwnerOrReadOnly
from .models import Review, ViewingLog
from .serializers import ReviewSerializer, ViewingLogSerializer


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.select_related('user', 'performance__work', 'performance__theater')
    serializer_class = ReviewSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ViewingLogViewSet(ModelViewSet):
    serializer_class = ViewingLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ViewingLog.objects.filter(
            user=self.request.user
        ).select_related('performance__work', 'performance__theater')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
