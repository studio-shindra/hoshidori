import json
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import SimpleTestCase, TestCase, override_settings
from rest_framework.test import APIClient

from .google_places import search_food_places, search_theater_place
from .models import Theater


class GooglePlacesTests(SimpleTestCase):
    def setUp(self):
        cache.clear()

    @override_settings(GOOGLE_PLACES_API_KEY='test-key')
    @patch('theaters.google_places.urlopen')
    def test_normalizes_text_search_results(self, mocked_urlopen):
        mocked_urlopen.side_effect = [
            BytesIO(json.dumps({
                'places': [{
                    'id': 'theater-1',
                    'displayName': {'text': '本多劇場'},
                    'location': {'latitude': 35.661, 'longitude': 139.668},
                }],
            }).encode()),
            BytesIO(json.dumps({
                'places': [{
                    'id': 'place-1',
                    'displayName': {'text': '終演後食堂'},
                    'formattedAddress': '東京都世田谷区北沢1-2-3',
                    'primaryTypeDisplayName': {'text': '居酒屋'},
                    'googleMapsUri': 'https://maps.google.com/?cid=1',
                    'location': {'latitude': 35.6614, 'longitude': 139.6683},
                }],
            }).encode()),
        ]

        results = search_food_places(SimpleNamespace(
            name='本多劇場', address='東京都世田谷区北沢2-10-15', area_name='下北沢',
        ))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], '終演後食堂')
        self.assertEqual(results[0]['category'], '居酒屋')
        self.assertEqual(results[0]['source'], 'google_places')
        self.assertIn('徒歩約', results[0]['distance_note'])
        request = mocked_urlopen.call_args_list[1].args[0]
        self.assertEqual(request.headers['X-goog-api-key'], 'test-key')
        self.assertIn('places.displayName', request.headers['X-goog-fieldmask'])
        self.assertIn('places:searchNearby', request.full_url)

    @override_settings(GOOGLE_PLACES_API_KEY='')
    @patch('theaters.google_places.urlopen')
    def test_does_not_call_google_without_key(self, mocked_urlopen):
        results = search_food_places(SimpleNamespace(
            name='本多劇場', address='', area_name='下北沢',
        ))

        self.assertEqual(results, [])
        mocked_urlopen.assert_not_called()

    @override_settings(GOOGLE_PLACES_API_KEY='test-key')
    @patch('theaters.google_places.urlopen')
    def test_returns_live_theater_photo_with_attribution(self, mocked_urlopen):
        mocked_urlopen.side_effect = [
            BytesIO(json.dumps({
                'places': [{
                    'id': 'theater-1',
                    'displayName': {'text': '本田劇場'},
                    'formattedAddress': '東京都世田谷区北沢2-10-15',
                    'googleMapsUri': 'https://maps.google.com/?cid=2',
                    'location': {'latitude': 35.661, 'longitude': 139.668},
                    'photos': [{
                        'name': 'places/theater-1/photos/photo-1',
                        'googleMapsUri': 'https://maps.google.com/photo/1',
                        'authorAttributions': [{
                            'displayName': '写真提供者',
                            'uri': 'https://maps.google.com/profile/1',
                        }],
                    }],
                }],
            }).encode()),
            BytesIO(json.dumps({'photoUri': 'https://lh3.googleusercontent.com/photo'}).encode()),
        ]

        result = search_theater_place(SimpleNamespace(
            name='本田劇場', address='東京都世田谷区北沢2-10-15', area_name='下北沢',
        ))

        self.assertEqual(result['photo_uri'], 'https://lh3.googleusercontent.com/photo')
        self.assertEqual(result['location']['latitude'], 35.661)
        self.assertEqual(result['author_attributions'][0]['display_name'], '写真提供者')
        self.assertEqual(mocked_urlopen.call_count, 2)


class TheaterRegistrationTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username='venue-editor', password='password')
        self.other = user_model.objects.create_user(username='other-editor', password='password')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_authenticated_user_can_register_pending_theater(self):
        response = self.client.post('/api/theaters/register/', {
            'name': '路地裏劇場',
            'address': '東京都世田谷区北沢1-2-3',
            'google_place_id': 'place-new-theater',
        }, format='json')

        self.assertEqual(response.status_code, 201)
        theater = Theater.objects.get(google_place_id='place-new-theater')
        self.assertEqual(theater.created_by, self.user)
        self.assertFalse(theater.is_approved)
        self.assertTrue(theater.slug)
        self.assertTrue(response.data['was_created'])

    def test_register_returns_existing_place_instead_of_duplicate(self):
        theater = Theater.objects.create(
            name='既存劇場', slug='existing-theater',
            address='東京都新宿区1-2-3', google_place_id='existing-place',
        )
        response = self.client.post('/api/theaters/register/', {
            'name': '既存劇場',
            'address': '東京都新宿区1-2-3',
            'google_place_id': 'existing-place',
        }, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], theater.id)
        self.assertFalse(response.data['was_created'])
        self.assertEqual(Theater.objects.count(), 1)

    def test_other_user_cannot_edit_pending_theater(self):
        theater = Theater.objects.create(
            name='登録者だけが直せる劇場', created_by=self.user, is_approved=False,
        )
        self.client.force_authenticate(self.other)
        response = self.client.patch(
            f'/api/theaters/{theater.slug}/', {'name': '勝手な変更'}, format='json',
        )

        self.assertEqual(response.status_code, 403)
