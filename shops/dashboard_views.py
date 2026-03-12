from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsShopUser
from .models import CouponUseLog, Shop, ShopClickLog


class ShopDashboardView(APIView):
    permission_classes = [IsShopUser]

    def get(self, request):
        shop = Shop.objects.filter(owner=request.user).first()
        if not shop:
            return Response({'error': 'shop_not_found'}, status=404)

        today = timezone.now().date()

        coupon_logs = CouponUseLog.objects.filter(coupon__shop=shop)
        coupon_use_total = coupon_logs.count()
        coupon_use_today = coupon_logs.filter(used_at__date=today).count()

        click_total = ShopClickLog.objects.filter(shop=shop).count()
        click_today = ShopClickLog.objects.filter(
            shop=shop, created_at__date=today,
        ).count()

        recent_coupon_uses = coupon_logs.select_related('coupon').order_by('-used_at')[:10]
        recent_list = [
            {
                'id': log.id,
                'coupon_title': log.coupon.title,
                'used_at': log.used_at.isoformat(),
                'performance_id': log.performance_id,
            }
            for log in recent_coupon_uses
        ]

        seven_days_ago = today - timedelta(days=6)
        daily_counts = (
            coupon_logs
            .filter(used_at__date__gte=seven_days_ago)
            .annotate(date=TruncDate('used_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )
        daily_map = {str(row['date']): row['count'] for row in daily_counts}
        daily_coupon_use_counts = []
        for i in range(7):
            d = seven_days_ago + timedelta(days=i)
            daily_coupon_use_counts.append({
                'date': str(d),
                'count': daily_map.get(str(d), 0),
            })

        return Response({
            'shop_id': shop.id,
            'shop_name': shop.name,
            'coupon_use_total': coupon_use_total,
            'coupon_use_today': coupon_use_today,
            'click_total': click_total,
            'click_today': click_today,
            'recent_coupon_uses': recent_list,
            'daily_coupon_use_counts': daily_coupon_use_counts,
        })
