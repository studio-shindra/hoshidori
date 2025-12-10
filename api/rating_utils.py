from django.db.models import Sum, Count
from .models import ViewingLog, WorkRating, Work


def calculate_avg_rating(work: Work):
    """ViewingLog と WorkRating を合算した平均を返す"""
    logs = ViewingLog.objects.filter(work=work, rating__isnull=False).aggregate(
        sum=Sum('rating'), count=Count('rating')
    )
    extras = WorkRating.objects.filter(work=work).aggregate(
        sum=Sum('rating'), count=Count('rating')
    )

    total_sum = (logs['sum'] or 0) + (extras['sum'] or 0)
    total_count = (logs['count'] or 0) + (extras['count'] or 0)

    if total_count == 0:
        return None

    return round(float(total_sum) / float(total_count), 1)


def add_rating_entry(work: Work, rating: float, user=None):
    """ゲスト/ユーザーの評価を保存し、最新平均を返す"""
    WorkRating.objects.create(work=work, user=user, rating=rating)
    return calculate_avg_rating(work)
