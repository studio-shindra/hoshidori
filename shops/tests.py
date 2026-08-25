from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from reviews.models import ViewingLog
from theaters.models import Theater
from works.models import Performance, Work

from .models import Shop, TheaterShop


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


class RecognizedShopTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.theater = Theater.objects.create(name='認定劇場', slug='recognized-theater')

    def test_recognized_endpoint_excludes_paid_featured_links(self):
        recognized = Shop.objects.create(name='認定食堂', slug='recognized-diner')
        sponsored = Shop.objects.create(name='おすすめ酒場', slug='sponsored-bar')
        TheaterShop.objects.create(theater=self.theater, shop=recognized, is_featured=False)
        TheaterShop.objects.create(theater=self.theater, shop=sponsored, is_featured=True)

        response = self.client.get('/api/shops/recognized/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual([shop['name'] for shop in response.data], ['認定食堂'])

    def test_shop_list_orders_sponsored_then_recognized_then_standard(self):
        standard = Shop.objects.create(name='通常書店', slug='standard-bookstore')
        recognized = Shop.objects.create(name='認定食堂', slug='recognized-diner')
        sponsored = Shop.objects.create(name='おすすめ酒場', slug='sponsored-bar')
        TheaterShop.objects.create(theater=self.theater, shop=recognized, is_featured=False)
        TheaterShop.objects.create(theater=self.theater, shop=sponsored, is_featured=True)

        response = self.client.get('/api/shops/')

        self.assertEqual(response.status_code, 200)
        shops = response.data['results']
        self.assertEqual(
            [shop['name'] for shop in shops],
            ['おすすめ酒場', '認定食堂', '通常書店'],
        )
        self.assertEqual(
            [shop['listing_tier'] for shop in shops],
            ['sponsored', 'recognized', 'standard'],
        )
