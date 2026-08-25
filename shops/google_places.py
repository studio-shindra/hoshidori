import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.cache import cache


PLACES_TEXT_SEARCH_URL = 'https://places.googleapis.com/v1/places:searchText'
PLACES_DETAILS_URL = 'https://places.googleapis.com/v1/places/{place_id}'
SHOP_FIELD_MASK = ','.join([
    'id',
    'displayName',
    'formattedAddress',
    'googleMapsUri',
    'photos',
])
SHOP_SEARCH_FIELD_MASK = ','.join(f'places.{field}' for field in SHOP_FIELD_MASK.split(','))


def _cache_key(shop):
    identity = ':'.join([
        getattr(shop, 'google_place_id', ''),
        shop.name,
        shop.address,
        settings.GOOGLE_PLACES_API_KEY,
    ])
    digest = hashlib.sha1(identity.encode('utf-8')).hexdigest()
    return f'google-places:shop:{digest}'


def _request_json(request):
    try:
        with urlopen(request, timeout=4) as response:
            return json.load(response)
    except (HTTPError, URLError, TimeoutError, ValueError):
        return None


def _photo_result(place, api_key):
    result = {
        'source': 'google_places',
        'place_id': place.get('id', ''),
        'name': place.get('displayName', {}).get('text', ''),
        'address': place.get('formattedAddress', ''),
        'google_maps_uri': place.get('googleMapsUri', ''),
        'photo_uri': '',
        'photo_google_maps_uri': '',
        'author_attributions': [],
    }
    photos = place.get('photos') or []
    if not photos or not photos[0].get('name'):
        return result

    photo = photos[0]
    media_url = f"https://places.googleapis.com/v1/{photo['name']}/media?{urlencode({'maxWidthPx': 1200, 'skipHttpRedirect': 'true', 'key': api_key})}"
    media = _request_json(Request(media_url))
    if not media:
        return result

    result['photo_uri'] = media.get('photoUri', '')
    result['photo_google_maps_uri'] = photo.get('googleMapsUri', '')
    result['author_attributions'] = [
        {
            'display_name': attribution.get('displayName', ''),
            'uri': attribution.get('uri', ''),
            'photo_uri': attribution.get('photoUri', ''),
        }
        for attribution in photo.get('authorAttributions', [])
        if attribution.get('displayName')
    ]
    return result


def search_shop_place(shop):
    """Return a live Google match and short-lived photo URL for one listed shop."""
    api_key = settings.GOOGLE_PLACES_API_KEY
    if not api_key or not shop.name:
        return None

    cache_key = _cache_key(shop)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    headers = {
        'X-Goog-Api-Key': api_key,
        'X-Goog-FieldMask': SHOP_FIELD_MASK,
    }
    place = None
    if shop.google_place_id:
        details_url = PLACES_DETAILS_URL.format(place_id=quote(shop.google_place_id, safe=''))
        place = _request_json(Request(details_url, headers=headers))

    if not place:
        payload = json.dumps({
            'textQuery': f'{shop.name} {shop.address}'.strip(),
            'languageCode': 'ja',
            'regionCode': 'JP',
            'maxResultCount': 1,
        }).encode('utf-8')
        place = _request_json(Request(
            PLACES_TEXT_SEARCH_URL,
            data=payload,
            method='POST',
            headers={
                'Content-Type': 'application/json',
                'X-Goog-Api-Key': api_key,
                'X-Goog-FieldMask': SHOP_SEARCH_FIELD_MASK,
            },
        ))
        place = ((place or {}).get('places') or [None])[0]

    result = _photo_result(place, api_key) if place else None
    cache.set(cache_key, result, 900)
    return result


def attach_google_place_data(shops):
    """Attach transient Google photo data without replacing an owned shop image."""
    shops = list(shops)
    targets = [shop for shop in shops if not shop.image_url and not shop.image]
    if not targets:
        return shops

    with ThreadPoolExecutor(max_workers=min(5, len(targets))) as executor:
        places = executor.map(search_shop_place, targets)
    for shop, place in zip(targets, places):
        shop._google_place_data = place or {}
    return shops
