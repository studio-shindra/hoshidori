from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from shops.models import Shop, TheaterShop
from theaters.models import Theater
from works.models import Performance, Work

from .models import Review, ReviewReport, UserBlock, ViewingLog


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


class ReviewSafetyTests(TestCase):
    def setUp(self):
        self.author = get_user_model().objects.create_user(
            username='author', password='test-password', display_name='投稿者',
        )
        self.viewer = get_user_model().objects.create_user(
            username='viewer', password='test-password', display_name='閲覧者',
        )
        theater = Theater.objects.create(
            name='テスト劇場', slug='safety-theater', area_name='東京',
        )
        work = Work.objects.create(title='安全機能テスト', created_by=self.author)
        self.performance = Performance.objects.create(
            work=work, theater=theater, created_by=self.author, is_approved=True,
        )
        self.review = Review.objects.create(
            user=self.author, performance=self.performance, body='心に残る舞台でした',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.viewer)

    def test_objectionable_review_is_rejected(self):
        response = self.client.post('/api/reviews/', {
            'performance': self.performance.id,
            'body': 'お前なんか死 ね',
        }, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('body', response.data)

    def test_review_can_be_reported(self):
        response = self.client.post(f'/api/reviews/{self.review.id}/report/', {
            'reason': 'harassment',
            'details': '個人を攻撃しています',
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertTrue(ReviewReport.objects.filter(
            reporter=self.viewer, review=self.review, status='pending',
        ).exists())

    def test_block_hides_reviews_and_can_be_removed(self):
        block_response = self.client.post(
            f'/api/reviews/{self.review.id}/block-user/', {}, format='json',
        )
        self.assertEqual(block_response.status_code, 201)
        block = UserBlock.objects.get(blocker=self.viewer, blocked=self.author)

        list_response = self.client.get(
            f'/api/reviews/?work={self.performance.work_id}',
        )
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.data['count'], 0)

        latest_response = self.client.get('/api/reviews/latest/')
        self.assertEqual(latest_response.status_code, 200)
        self.assertEqual(len(latest_response.data), 0)

        blocks_response = self.client.get('/api/user-blocks/')
        self.assertEqual(blocks_response.status_code, 200)
        self.assertEqual(blocks_response.data['results'][0]['blocked_display_name'], '投稿者')

        delete_response = self.client.delete(f'/api/user-blocks/{block.id}/')
        self.assertEqual(delete_response.status_code, 204)
        self.assertFalse(UserBlock.objects.filter(pk=block.id).exists())
