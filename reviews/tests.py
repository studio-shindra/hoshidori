from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from shops.models import Shop, TheaterShop
from theaters.models import Theater
from works.models import Performance, Work

from .models import Review, ViewingLog


class AfterShopViewingLogTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='theatergoer', password='test-password',
        )
        self.theater = Theater.objects.create(
            name='本田劇場', slug='honda-theater', area_name='下北沢',
        )
        self.work = Work.objects.create(title='星の公演', created_by=self.user)
        self.performance = Performance.objects.create(
            work=self.work,
            theater=self.theater,
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 31),
            created_by=self.user,
            is_approved=True,
        )
        self.shop = Shop.objects.create(name='感想戦酒場', slug='kansosen-sakaba')
        TheaterShop.objects.create(theater=self.theater, shop=self.shop)
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_after_shop_is_saved_and_returned_with_review(self):
        response = self.client.post('/api/viewing-logs/', {
            'performance': self.performance.id,
            'status': 'watched',
            'watched_on': '2026-08-24',
            'after_shop': self.shop.id,
            'memo': '終演後に話した',
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['after_shop'], self.shop.id)
        self.assertEqual(response.data['after_shop_name'], self.shop.name)
        self.assertEqual(
            ViewingLog.objects.get(user=self.user).after_shop,
            self.shop,
        )

        Review.objects.create(
            user=self.user,
            performance=self.performance,
            body='よい舞台だった',
            rating_overall=5,
        )
        review_response = self.client.get(
            f'/api/reviews/?work={self.work.id}',
        )

        self.assertEqual(review_response.status_code, 200)
        review = review_response.data['results'][0]
        self.assertEqual(review['after_shop'], self.shop.id)
        self.assertEqual(review['after_shop_name'], self.shop.name)
        self.assertEqual(review['after_shop_slug'], self.shop.slug)

    def test_calendar_and_archive_meta_return_month_and_real_counts(self):
        ViewingLog.objects.create(
            user=self.user,
            performance=self.performance,
            status='watched',
            watched_on=date(2026, 8, 24),
        )

        calendar_response = self.client.get(
            '/api/viewing-logs/calendar/?year=2026&month=8',
        )
        self.assertEqual(calendar_response.status_code, 200)
        self.assertEqual(len(calendar_response.data['results']), 1)
        self.assertEqual(calendar_response.data['results'][0]['work_title'], '星の公演')

        meta_response = self.client.get('/api/viewing-logs/archive-meta/')
        self.assertEqual(meta_response.status_code, 200)
        self.assertEqual(meta_response.data['years'][0], {
            'year': 2026,
            'planned': 0,
            'watched': 1,
        })

    def test_watched_log_rejects_future_date(self):
        response = self.client.post('/api/viewing-logs/', {
            'performance': self.performance.id,
            'status': 'watched',
            'watched_on': str(timezone.localdate() + timedelta(days=1)),
        }, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('watched_on', response.data)
