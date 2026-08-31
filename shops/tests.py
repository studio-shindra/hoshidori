import json
import hashlib
import hmac
import time
from io import BytesIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from reviews.models import ViewingLog
from theaters.models import Theater
from works.models import Performance, Work

from .models import Shop, ShopSubscription, TheaterShop
from .google_places import search_shop_place
from .serializers import ShopSerializer


class ShopDashboardTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            username='shop-owner', password='test-password', role='shop',
        )
        self.visitor = user_model.objects.create_user(
            username='visitor', password='test-password',
        )
        self.shop = Shop.objects.create(
            name='終演後食堂', slug='after-show-diner', owner=self.owner,
        )
        theater = Theater.objects.create(name='劇場', slug='theater')
        work = Work.objects.create(title='舞台作品', created_by=self.visitor)
        performance = Performance.objects.create(
            work=work,
            theater=theater,
            start_date=timezone.localdate(),
            end_date=timezone.localdate(),
            created_by=self.visitor,
            is_approved=True,
        )
        ViewingLog.objects.create(
            user=self.visitor,
            performance=performance,
            status='watched',
            watched_on=timezone.localdate(),
            after_shop=self.shop,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.owner)

    def test_dashboard_reports_after_viewing_referrals(self):
        response = self.client.get('/api/dashboard/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['after_viewing_total'], 1)
        self.assertEqual(response.data['after_viewing_this_month'], 1)
        self.assertEqual(response.data['top_works'], [
            {'work_title': '舞台作品', 'count': 1},
        ])
        self.assertEqual(
            response.data['daily_after_viewing_counts'][-1]['count'],
            1,
        )

    def test_owner_can_update_shop_profile(self):
        response = self.client.patch('/api/dashboard/', {
            'description': '観劇後に立ち寄れる食堂です。',
            'benefit_text': '半券提示で小鉢サービス',
        }, format='json')

        self.assertEqual(response.status_code, 200)
        self.shop.refresh_from_db()
        self.assertEqual(self.shop.benefit_text, '半券提示で小鉢サービス')


class ShopApplicationTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username='new-shop-owner', email='shop@example.com', password='test-password',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_application_creates_inactive_shop_and_shop_role(self):
        theater = Theater.objects.create(name='申請先劇場', slug='application-theater')
        response = self.client.post('/api/shop-application/', {
            'name': '観劇酒場',
            'category': '居酒屋',
            'address': '東京都世田谷区北沢1-1-1',
            'google_place_id': 'place-application-1',
            'theater_ids': [theater.id],
        }, format='json')

        self.assertEqual(response.status_code, 201)
        shop = Shop.objects.get(owner=self.user)
        self.assertFalse(shop.is_active)
        self.assertFalse(shop.is_featured)
        self.assertTrue(TheaterShop.objects.filter(shop=shop, theater=theater).exists())
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, 'shop')
        self.assertFalse(Shop.objects.filter(is_active=True, pk=shop.pk).exists())

    def test_duplicate_google_place_is_rejected(self):
        Shop.objects.create(
            name='登録済み店', slug='registered-shop', google_place_id='same-place',
        )
        response = self.client.post('/api/shop-application/', {
            'name': '別名の同じ店',
            'address': '東京都世田谷区北沢1-1-1',
            'google_place_id': 'same-place',
        }, format='json')

        self.assertEqual(response.status_code, 400)


@override_settings(
    STRIPE_SECRET_KEY='sk_test_example',
    STRIPE_SHOP_PRICE_ID='price_example',
    STRIPE_WEBHOOK_SECRET='whsec_example',
    FRONTEND_URL='https://example.com',
)
class ShopBillingTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            username='billing-owner', email='billing@example.com',
            password='test-password', role='shop',
        )
        self.shop = Shop.objects.create(
            name='課金酒場', slug='billing-bar', owner=self.owner, is_active=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.owner)

    @patch('shops.dashboard_views.stripe_request')
    def test_checkout_uses_recommended_monthly_price(self, mocked_stripe):
        mocked_stripe.return_value = {'url': 'https://checkout.stripe.com/test'}

        response = self.client.post('/api/dashboard/checkout/', {}, format='json')

        self.assertEqual(response.status_code, 200)
        payload = mocked_stripe.call_args.args[1]
        self.assertEqual(payload['line_items[0][price]'], 'price_example')
        self.assertEqual(payload['subscription_data[metadata][shop_id]'], str(self.shop.id))

    def test_subscription_webhook_enables_recommended_listing(self):
        payload = json.dumps({
            'type': 'customer.subscription.updated',
            'data': {'object': {
                'id': 'sub_example',
                'customer': 'cus_example',
                'status': 'active',
                'metadata': {'shop_id': str(self.shop.id)},
                'current_period_start': 1700000000,
                'current_period_end': 1702678400,
            }},
        }).encode('utf-8')
        timestamp = int(time.time())
        signature = hmac.new(
            b'whsec_example',
            f'{timestamp}.'.encode('utf-8') + payload,
            hashlib.sha256,
        ).hexdigest()

        client = APIClient()
        response = client.post(
            '/api/stripe/webhook/',
            data=payload,
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE=f't={timestamp},v1={signature}',
        )

        self.assertEqual(response.status_code, 200)
        self.shop.refresh_from_db()
        self.assertTrue(self.shop.is_featured)
        self.assertTrue(ShopSubscription.objects.filter(
            shop=self.shop, stripe_subscription_id='sub_example', status='active',
        ).exists())


class RecognizedShopTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.theater = Theater.objects.create(name='認定劇場', slug='recognized-theater')

    def test_recognized_endpoint_excludes_paid_featured_links(self):
        recognized = Shop.objects.create(name='認定食堂', slug='recognized-diner')
        sponsored = Shop.objects.create(name='おすすめ酒場', slug='sponsored-bar')
        listed = Shop.objects.create(name='無料掲載店', slug='listed-diner')
        TheaterShop.objects.create(
            theater=self.theater, shop=recognized,
            is_featured=False, is_recognized=True,
        )
        TheaterShop.objects.create(theater=self.theater, shop=listed)
        TheaterShop.objects.create(theater=self.theater, shop=sponsored, is_featured=True)

        response = self.client.get('/api/shops/recognized/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual([shop['name'] for shop in response.data], ['認定食堂'])

    def test_shop_list_orders_sponsored_then_recognized_then_standard(self):
        standard = Shop.objects.create(name='通常書店', slug='standard-bookstore')
        recognized = Shop.objects.create(name='認定食堂', slug='recognized-diner')
        sponsored = Shop.objects.create(name='おすすめ酒場', slug='sponsored-bar')
        listed = Shop.objects.create(name='無料掲載店', slug='listed-diner')
        TheaterShop.objects.create(
            theater=self.theater, shop=recognized,
            is_featured=False, is_recognized=True,
        )
        TheaterShop.objects.create(theater=self.theater, shop=listed)
        TheaterShop.objects.create(theater=self.theater, shop=sponsored, is_featured=True)

        response = self.client.get('/api/shops/')

        self.assertEqual(response.status_code, 200)
        shops = response.data['results']
        self.assertEqual(
            [shop['name'] for shop in shops],
            ['おすすめ酒場', '認定食堂', '無料掲載店', '通常書店'],
        )
        self.assertEqual(
            [shop['listing_tier'] for shop in shops],
            ['sponsored', 'recognized', 'listed', 'standard'],
        )


@override_settings(GOOGLE_PLACES_API_KEY='test-key')
class ShopGooglePlacesTests(TestCase):
    def setUp(self):
        cache.clear()
        self.shop = Shop.objects.create(
            name='燗味処',
            slug='kanmidokoro',
            address='東京都世田谷区北沢2-32-8',
        )

    @patch('shops.google_places.urlopen')
    def test_searches_by_name_and_address_and_returns_photo_attribution(self, mocked_urlopen):
        mocked_urlopen.side_effect = [
            BytesIO(json.dumps({
                'places': [{
                    'id': 'google-shop-1',
                    'displayName': {'text': '燗味処'},
                    'formattedAddress': self.shop.address,
                    'googleMapsUri': 'https://maps.google.com/shop/1',
                    'photos': [{
                        'name': 'places/google-shop-1/photos/photo-1',
                        'googleMapsUri': 'https://maps.google.com/photo/1',
                        'authorAttributions': [{
                            'displayName': '撮影者',
                            'uri': 'https://maps.google.com/contributor/1',
                        }],
                    }],
                }],
            }).encode()),
            BytesIO(json.dumps({
                'photoUri': 'https://lh3.googleusercontent.com/shop-photo',
            }).encode()),
        ]

        result = search_shop_place(self.shop)

        self.assertEqual(result['place_id'], 'google-shop-1')
        self.assertEqual(result['photo_uri'], 'https://lh3.googleusercontent.com/shop-photo')
        self.assertEqual(result['author_attributions'][0]['display_name'], '撮影者')
        search_request = mocked_urlopen.call_args_list[0].args[0]
        self.assertIn('燗味処', json.loads(search_request.data)['textQuery'])
        self.assertIn('places.photos', search_request.headers['X-goog-fieldmask'])

    def test_serializer_prefers_owned_image_over_google_photo(self):
        self.shop.image_url = 'https://example.com/owned.jpg'
        self.shop._google_place_data = {
            'photo_uri': 'https://example.com/google.jpg',
            'author_attributions': [{'display_name': '撮影者'}],
        }

        data = ShopSerializer(self.shop).data

        self.assertEqual(data['image_src'], 'https://example.com/owned.jpg')
        self.assertEqual(data['image_source'], 'owned')

    def test_serializer_uses_google_photo_when_owned_image_is_missing(self):
        self.shop._google_place_data = {
            'photo_uri': 'https://example.com/google.jpg',
            'photo_google_maps_uri': 'https://maps.google.com/photo/1',
            'author_attributions': [{'display_name': '撮影者'}],
        }

        data = ShopSerializer(self.shop).data

        self.assertEqual(data['image_src'], 'https://example.com/google.jpg')
        self.assertEqual(data['image_source'], 'google_places')
        self.assertEqual(data['google_photo_maps_uri'], 'https://maps.google.com/photo/1')
        self.assertEqual(data['google_photo_attributions'][0]['display_name'], '撮影者')
