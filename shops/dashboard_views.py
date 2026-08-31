import json
from datetime import datetime, timedelta, timezone as datetime_timezone

from django.conf import settings
from django.db.models import Count
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsShopUser
from .google_places import search_shop_candidates
from .models import Shop, ShopClickLog, ShopPlan, ShopSubscription
from .serializers import ShopApplicationSerializer, ShopOwnerSerializer
from .stripe_client import StripeRequestError, stripe_request, verify_webhook_signature


RECOMMENDED_PLAN_NAME = 'ホシドリおすすめ店'
RECOMMENDED_PLAN_PRICE = 5000


def _recommended_plan():
    plan, _ = ShopPlan.objects.get_or_create(
        name=RECOMMENDED_PLAN_NAME,
        defaults={
            'monthly_price': RECOMMENDED_PLAN_PRICE,
            'description': '検索結果や劇場周辺で優先表示される月額プランです。',
            'is_active': True,
        },
    )
    changed_fields = []
    if plan.monthly_price != RECOMMENDED_PLAN_PRICE:
        plan.monthly_price = RECOMMENDED_PLAN_PRICE
        changed_fields.append('monthly_price')
    if not plan.is_active:
        plan.is_active = True
        changed_fields.append('is_active')
    if changed_fields:
        plan.save(update_fields=changed_fields)
    return plan


def _timestamp(value):
    if not value:
        return None
    return datetime.fromtimestamp(value, tz=datetime_timezone.utc)


def _subscription_payload(shop):
    subscription = shop.subscriptions.order_by('-created_at').first()
    if not subscription:
        return None
    return {
        'status': subscription.status,
        'plan_name': subscription.plan.name,
        'monthly_price': subscription.plan.monthly_price,
        'current_period_end': subscription.current_period_end,
        'can_manage_billing': bool(subscription.stripe_customer_id),
    }


def _sync_subscription(data, fallback_shop=None):
    metadata = data.get('metadata') or {}
    shop_id = metadata.get('shop_id')
    shop = fallback_shop
    if not shop and shop_id:
        shop = Shop.objects.filter(pk=shop_id).first()
    if not shop and data.get('id'):
        existing = ShopSubscription.objects.filter(
            stripe_subscription_id=data['id'],
        ).select_related('shop').first()
        shop = existing.shop if existing else None
    if not shop and data.get('customer'):
        existing = ShopSubscription.objects.filter(
            stripe_customer_id=data['customer'],
        ).select_related('shop').first()
        shop = existing.shop if existing else None
    if not shop:
        return None

    plan = _recommended_plan()
    subscription_id = data.get('id', '')
    subscription = None
    if subscription_id:
        subscription = ShopSubscription.objects.filter(
            stripe_subscription_id=subscription_id,
        ).first()
    if not subscription:
        subscription = ShopSubscription.objects.filter(shop=shop).order_by('-created_at').first()
    if not subscription:
        subscription = ShopSubscription(shop=shop, plan=plan)

    subscription.plan = plan
    subscription.status = data.get('status') or subscription.status or 'incomplete'
    subscription.stripe_customer_id = data.get('customer') or subscription.stripe_customer_id
    subscription.stripe_subscription_id = subscription_id or subscription.stripe_subscription_id
    subscription.current_period_start = _timestamp(data.get('current_period_start'))
    subscription.current_period_end = _timestamp(data.get('current_period_end'))
    subscription.save()

    shop.is_featured = subscription.status in ('active', 'trialing')
    shop.save(update_fields=['is_featured', 'updated_at'])
    return subscription


class ShopApplicationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        shop = Shop.objects.filter(owner=request.user).first()
        return Response({
            'has_application': bool(shop),
            'shop': ShopOwnerSerializer(shop).data if shop else None,
        })

    def post(self, request):
        serializer = ShopApplicationSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        shop = serializer.save()
        return Response(ShopOwnerSerializer(shop).data, status=status.HTTP_201_CREATED)


class ShopPlaceCandidateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'results': search_shop_candidates(request.query_params.get('q', ''))})


class ShopDashboardView(APIView):
    permission_classes = [IsShopUser]

    def _shop(self, request):
        return Shop.objects.filter(owner=request.user).first()

    def get(self, request):
        shop = self._shop(request)
        if not shop:
            return Response({'error': 'shop_not_found'}, status=404)

        today = timezone.localdate()
        after_logs = shop.after_viewing_logs.filter(status='watched')
        clicks = ShopClickLog.objects.filter(shop=shop)
        top_works = (
            after_logs.values('performance__work__title')
            .annotate(count=Count('id'))
            .order_by('-count', 'performance__work__title')[:10]
        )
        seven_days_ago = today - timedelta(days=6)
        daily_counts = (
            after_logs.filter(watched_on__gte=seven_days_ago)
            .values('watched_on').annotate(count=Count('id')).order_by('watched_on')
        )
        daily_map = {str(row['watched_on']): row['count'] for row in daily_counts}
        click_breakdown = {
            row['clicked_target'] or 'detail': row['count']
            for row in clicks.values('clicked_target').annotate(count=Count('id'))
        }
        return Response({
            'shop': ShopOwnerSerializer(shop).data,
            'subscription': _subscription_payload(shop),
            'recommended_plan': {
                'name': RECOMMENDED_PLAN_NAME,
                'monthly_price': RECOMMENDED_PLAN_PRICE,
                'stripe_ready': bool(settings.STRIPE_SECRET_KEY and settings.STRIPE_SHOP_PRICE_ID),
            },
            'after_viewing_total': after_logs.count(),
            'after_viewing_this_month': after_logs.filter(
                watched_on__gte=today.replace(day=1),
            ).count(),
            'click_total': clicks.count(),
            'click_today': clicks.filter(created_at__date=today).count(),
            'click_breakdown': click_breakdown,
            'top_works': [
                {'work_title': row['performance__work__title'], 'count': row['count']}
                for row in top_works
            ],
            'daily_after_viewing_counts': [
                {
                    'date': str(seven_days_ago + timedelta(days=index)),
                    'count': daily_map.get(str(seven_days_ago + timedelta(days=index)), 0),
                }
                for index in range(7)
            ],
        })

    def patch(self, request):
        shop = self._shop(request)
        if not shop:
            return Response({'error': 'shop_not_found'}, status=404)
        serializer = ShopOwnerSerializer(shop, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ShopImageUploadView(APIView):
    permission_classes = [IsShopUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        shop = Shop.objects.filter(owner=request.user).first()
        if not shop:
            return Response({'error': 'shop_not_found'}, status=404)
        image = request.FILES.get('image')
        if not image:
            return Response({'image': ['画像を選択してください。']}, status=400)
        if image.size > 8 * 1024 * 1024:
            return Response({'image': ['画像は8MB以下にしてください。']}, status=400)
        if image.content_type not in ('image/jpeg', 'image/png', 'image/webp'):
            return Response({'image': ['JPEG、PNG、WebPの画像を選択してください。']}, status=400)
        shop.image = image
        shop.image_url = ''
        shop.save(update_fields=['image', 'image_url', 'updated_at'])
        return Response(ShopOwnerSerializer(shop).data)


class ShopCheckoutView(APIView):
    permission_classes = [IsShopUser]

    def post(self, request):
        shop = Shop.objects.filter(owner=request.user).first()
        if not shop:
            return Response({'error': 'shop_not_found'}, status=404)
        if not shop.is_active:
            return Response({'error': 'approval_required'}, status=409)
        if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_SHOP_PRICE_ID:
            return Response({'error': 'stripe_not_configured'}, status=503)
        if shop.subscriptions.filter(status__in=['active', 'trialing']).exists():
            return Response({'error': 'already_subscribed'}, status=409)

        frontend_url = settings.FRONTEND_URL.rstrip('/')
        payload = {
            'mode': 'subscription',
            'line_items[0][price]': settings.STRIPE_SHOP_PRICE_ID,
            'line_items[0][quantity]': 1,
            'client_reference_id': str(shop.id),
            'customer_email': request.user.email,
            'metadata[shop_id]': str(shop.id),
            'subscription_data[metadata][shop_id]': str(shop.id),
            'success_url': f'{frontend_url}/dashboard?checkout=success',
            'cancel_url': f'{frontend_url}/dashboard?checkout=cancelled',
            'locale': 'ja',
        }
        try:
            session = stripe_request('/checkout/sessions', payload)
        except StripeRequestError as error:
            return Response({'error': 'stripe_error', 'detail': str(error)}, status=502)
        return Response({'url': session['url']})


class ShopBillingPortalView(APIView):
    permission_classes = [IsShopUser]

    def post(self, request):
        shop = Shop.objects.filter(owner=request.user).first()
        subscription = shop.subscriptions.order_by('-created_at').first() if shop else None
        if not subscription or not subscription.stripe_customer_id:
            return Response({'error': 'customer_not_found'}, status=404)
        try:
            portal = stripe_request('/billing_portal/sessions', {
                'customer': subscription.stripe_customer_id,
                'return_url': f"{settings.FRONTEND_URL.rstrip('/')}/dashboard",
            })
        except StripeRequestError as error:
            return Response({'error': 'stripe_error', 'detail': str(error)}, status=502)
        return Response({'url': portal['url']})


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.body
        if not verify_webhook_signature(payload, request.headers.get('Stripe-Signature', '')):
            return Response({'error': 'invalid_signature'}, status=400)
        try:
            event = json.loads(payload)
        except ValueError:
            return Response({'error': 'invalid_payload'}, status=400)

        event_type = event.get('type', '')
        data = (event.get('data') or {}).get('object') or {}
        if event_type == 'checkout.session.completed':
            shop_id = (data.get('metadata') or {}).get('shop_id') or data.get('client_reference_id')
            shop = Shop.objects.filter(pk=shop_id).first() if shop_id else None
            subscription_id = data.get('subscription')
            if shop and subscription_id:
                try:
                    subscription_data = stripe_request(
                        f'/subscriptions/{subscription_id}', method='GET',
                    )
                except StripeRequestError:
                    subscription_data = {
                        'id': subscription_id,
                        'customer': data.get('customer', ''),
                        'status': 'active',
                        'metadata': {'shop_id': str(shop.id)},
                    }
                _sync_subscription(subscription_data, fallback_shop=shop)
        elif event_type in (
            'customer.subscription.created',
            'customer.subscription.updated',
            'customer.subscription.deleted',
        ):
            _sync_subscription(data)
        elif event_type == 'invoice.payment_failed':
            subscription = ShopSubscription.objects.filter(
                stripe_subscription_id=data.get('subscription'),
            ).select_related('shop').first()
            if subscription:
                subscription.status = 'past_due'
                subscription.save(update_fields=['status'])
                subscription.shop.is_featured = False
                subscription.shop.save(update_fields=['is_featured', 'updated_at'])
        return Response({'received': True})
