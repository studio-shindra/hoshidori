from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Coupon, CouponUseLog, Shop, ShopClickLog
from .serializers import CouponSerializer, ShopSerializer


class ShopViewSet(ReadOnlyModelViewSet):
    queryset = Shop.objects.filter(is_active=True)
    serializer_class = ShopSerializer
    lookup_field = 'slug'
    permission_classes = [AllowAny]

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def click(self, request, slug=None):
        shop = self.get_object()
        ShopClickLog.objects.create(
            shop=shop,
            user=request.user if request.user.is_authenticated else None,
            source_type=request.data.get('source_type', ''),
            clicked_target=request.data.get('clicked_target', ''),
        )
        return Response({'detail': '記録しました。'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='coupons', permission_classes=[AllowAny])
    def coupons(self, request, slug=None):
        shop = self.get_object()
        coupons = Coupon.objects.filter(shop=shop, is_active=True)
        serializer = CouponSerializer(coupons, many=True)
        return Response(serializer.data)


class CouponViewSet(ReadOnlyModelViewSet):
    queryset = Coupon.objects.filter(is_active=True).select_related('shop')
    serializer_class = CouponSerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def use(self, request, pk=None):
        coupon = self.get_object()
        performance_id = request.data.get('performance')
        log = CouponUseLog.objects.create(
            coupon=coupon,
            user=request.user,
            performance_id=performance_id,
        )
        return Response({
            'detail': 'クーポンを利用しました。',
            'coupon_title': coupon.title,
            'used_at': log.used_at.isoformat(),
        }, status=status.HTTP_201_CREATED)
