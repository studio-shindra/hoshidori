from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Theater
from .serializers import TheaterSerializer


class TheaterViewSet(ReadOnlyModelViewSet):
    queryset = Theater.objects.filter(is_active=True)
    serializer_class = TheaterSerializer
    lookup_field = 'slug'
