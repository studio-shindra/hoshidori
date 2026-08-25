from datetime import timedelta

from django.db.models import Count
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsShopUser
from .models import Shop, ShopClickLog


class ShopDashboardView(APIView):
    permission_classes = [IsShopUser]

    def get(self, request):
        shop = Shop.objects.filter(owner=request.user).first()
        if not shop:
            return Response({'error': 'shop_not_found'}, status=404)

        today = timezone.localdate()

        after_logs = shop.after_viewing_logs.filter(status='watched')
        after_viewing_total = after_logs.count()
        after_viewing_this_month = after_logs.filter(
            watched_on__gte=today.replace(day=1),
        ).count()

        click_total = ShopClickLog.objects.filter(shop=shop).count()
        click_today = ShopClickLog.objects.filter(
            shop=shop, created_at__date=today,
        ).count()

        top_works = (
            after_logs
            .values('performance__work__title')
            .annotate(count=Count('id'))
            .order_by('-count', 'performance__work__title')[:10]
        )
        top_work_list = [
            {
                'work_title': row['performance__work__title'],
                'count': row['count'],
            }
            for row in top_works
        ]

        seven_days_ago = today - timedelta(days=6)
        daily_counts = (
            after_logs
            .filter(watched_on__gte=seven_days_ago)
            .values('watched_on')
            .annotate(count=Count('id'))
            .order_by('watched_on')
        )
        daily_map = {str(row['watched_on']): row['count'] for row in daily_counts}
        daily_after_viewing_counts = []
        for i in range(7):
            d = seven_days_ago + timedelta(days=i)
            daily_after_viewing_counts.append({
                'date': str(d),
                'count': daily_map.get(str(d), 0),
            })

        return Response({
            'shop_id': shop.id,
            'shop_name': shop.name,
            'after_viewing_total': after_viewing_total,
            'after_viewing_this_month': after_viewing_this_month,
            'click_total': click_total,
            'click_today': click_today,
            'top_works': top_work_list,
            'daily_after_viewing_counts': daily_after_viewing_counts,
        })
