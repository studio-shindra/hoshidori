from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from shops.models import TheaterShop
from shops.serializers import ShopSerializer
from .models import Theater
from .serializers import TheaterSerializer


class TheaterViewSet(ReadOnlyModelViewSet):
    queryset = Theater.objects.filter(is_active=True)
    serializer_class = TheaterSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get('q')
        if q:
            qs = qs.filter(name__icontains=q)
        return qs

    @action(detail=True, methods=['get'])
    def shops(self, request, slug=None):
        theater = self.get_object()
        theater_shops = TheaterShop.objects.filter(
            theater=theater, shop__is_active=True,
        ).select_related('shop').order_by('sort_order')
        shops = [ts.shop for ts in theater_shops]
        serializer = ShopSerializer(shops, many=True)
        return Response(serializer.data)
