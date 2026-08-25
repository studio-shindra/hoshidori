import hashlib
import json
import math
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus, urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.cache import cache


PLACES_TEXT_SEARCH_URL = 'https://places.googleapis.com/v1/places:searchText'
PLACES_NEARBY_SEARCH_URL = 'https://places.googleapis.com/v1/places:searchNearby'
PLACES_FIELD_MASK = ','.join([
    'places.id',
    'places.displayName',
    'places.formattedAddress',
    'places.primaryTypeDisplayName',
    'places.googleMapsUri',
    'places.location',
])
THEATER_FIELD_MASK = ','.join([
    'places.id',
    'places.displayName',
    'places.formattedAddress',
    'places.googleMapsUri',
    'places.photos',
    'places.location',
])
CANDIDATE_FIELD_MASK = ','.join([
    'places.id',
    'places.displayName',
    'places.formattedAddress',
    'places.primaryType',
    'places.primaryTypeDisplayName',
    'places.types',
    'places.googleMapsUri',
])


def _cache_key(prefix, theater, suffix=''):
    identity = f"{getattr(theater, 'slug', '')}:{theater.name}:{settings.GOOGLE_PLACES_API_KEY}:{suffix}"
    digest = hashlib.sha1(identity.encode('utf-8')).hexdigest()
    return f'google-places:{prefix}:{digest}'


def _walking_minutes(origin, destination):
    """Return a modest straight-line walking estimate for the short nearby list."""
    try:
        lat1 = math.radians(float(origin['latitude']))
        lon1 = math.radians(float(origin['longitude']))
        lat2 = math.radians(float(destination['latitude']))
        lon2 = math.radians(float(destination['longitude']))
    except (KeyError, TypeError, ValueError):
        return None

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    distance_m = 6371000 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return max(1, math.ceil(distance_m / 70))


def search_theater_candidates(query, limit=6):
    """Return live Google candidates for a user-entered theater name."""
    api_key = settings.GOOGLE_PLACES_API_KEY
    query = (query or '').strip()
    if not api_key or len(query) < 2:
        return []

    digest = hashlib.sha1(f'{query}:{api_key}:{limit}'.encode('utf-8')).hexdigest()
    cache_key = f'google-places:theater-candidates:{digest}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    payload = json.dumps({
        'textQuery': query,
        'includedType': 'performing_arts_theater',
        'strictTypeFiltering': False,
        'languageCode': 'ja',
        'regionCode': 'JP',
        'maxResultCount': limit,
    }).encode('utf-8')
    request = Request(
        PLACES_TEXT_SEARCH_URL,
        data=payload,
        method='POST',
        headers={
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': api_key,
            'X-Goog-FieldMask': CANDIDATE_FIELD_MASK,
        },
    )

    try:
        with urlopen(request, timeout=4) as response:
            data = json.load(response)
    except (HTTPError, URLError, TimeoutError, ValueError):
        return []

    results = []
    for place in data.get('places', []):
        place_id = place.get('id', '').strip()
        name = place.get('displayName', {}).get('text', '').strip()
        if not place_id or not name:
            continue
        results.append({
            'place_id': place_id,
            'name': name,
            'address': place.get('formattedAddress', '').strip(),
            'type': place.get('primaryTypeDisplayName', {}).get('text', '').strip(),
            'types': place.get('types') or [],
            'google_maps_uri': place.get('googleMapsUri', ''),
        })
    cache.set(cache_key, results, 300)
    return results


def search_food_places(theater, limit=5):
    """Return live Google Places results without persisting Places content."""
    api_key = settings.GOOGLE_PLACES_API_KEY
    if not api_key:
        return []

    cache_key = _cache_key('food', theater, limit)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    theater_place = search_theater_place(theater)
    theater_location = (theater_place or {}).get('location') or {}
    if not theater_location.get('latitude') or not theater_location.get('longitude'):
        return []

    payload = json.dumps({
        'includedTypes': ['restaurant', 'cafe', 'bar'],
        'languageCode': 'ja',
        'maxResultCount': limit,
        'rankPreference': 'DISTANCE',
        'locationRestriction': {
            'circle': {
                'center': theater_location,
                'radius': 800.0,
            },
        },
    }).encode('utf-8')
    request = Request(
        PLACES_NEARBY_SEARCH_URL,
        data=payload,
        method='POST',
        headers={
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': api_key,
            'X-Goog-FieldMask': PLACES_FIELD_MASK,
        },
    )

    try:
        with urlopen(request, timeout=4) as response:
            data = json.load(response)
    except (HTTPError, URLError, TimeoutError, ValueError):
        return []

    results = []
    for place in data.get('places', []):
        name = place.get('displayName', {}).get('text', '').strip()
        if not name:
            continue
        category = place.get('primaryTypeDisplayName', {}).get('text', '').strip()
        walk_minutes = _walking_minutes(theater_location, place.get('location') or {})
        results.append({
            'id': f"google:{place.get('id', name)}",
            'slug': None,
            'name': name,
            'category': category,
            'description': '',
            'address': place.get('formattedAddress', ''),
            'nearest_station': '',
            'distance_note': f'{theater.name}から徒歩約{walk_minutes}分' if walk_minutes else '',
            'benefit_text': '',
            'image_src': None,
            'google_map_url': place.get('googleMapsUri', ''),
            'after_viewing_count': 0,
            'is_featured': False,
            'is_want_to_go': False,
            'source': 'google_places',
            'listing_tier': 'google',
            'is_preview': False,
        })
    cache.set(cache_key, results, 600)
    return results


def search_theater_place(theater):
    """Return one live theater match and a short-lived Google photo URL."""
    api_key = settings.GOOGLE_PLACES_API_KEY
    if not api_key:
        return None

    cache_key = _cache_key('theater', theater)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    payload = json.dumps({
        'textQuery': f'{theater.name} {theater.address or theater.area_name}'.strip(),
        'languageCode': 'ja',
        'regionCode': 'JP',
        'maxResultCount': 1,
    }).encode('utf-8')
    request = Request(
        PLACES_TEXT_SEARCH_URL,
        data=payload,
        method='POST',
        headers={
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': api_key,
            'X-Goog-FieldMask': THEATER_FIELD_MASK,
        },
    )

    try:
        with urlopen(request, timeout=4) as response:
            data = json.load(response)
        place = (data.get('places') or [])[0]
    except (HTTPError, URLError, TimeoutError, ValueError, IndexError):
        return None

    result = {
        'source': 'google_places',
        'place_id': place.get('id', ''),
        'name': place.get('displayName', {}).get('text', ''),
        'address': place.get('formattedAddress', ''),
        'google_maps_uri': place.get('googleMapsUri', ''),
        'location': place.get('location') or {},
        'photo_uri': '',
        'photo_google_maps_uri': '',
        'author_attributions': [],
    }
    photos = place.get('photos') or []
    if not photos or not photos[0].get('name'):
        cache.set(cache_key, result, 900)
        return result

    photo = photos[0]
    media_url = f"https://places.googleapis.com/v1/{photo['name']}/media?{urlencode({'maxWidthPx': 1200, 'skipHttpRedirect': 'true', 'key': api_key})}"
    try:
        with urlopen(media_url, timeout=4) as response:
            media = json.load(response)
    except (HTTPError, URLError, TimeoutError, ValueError):
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
    cache.set(cache_key, result, 900)
    return result


def preview_food_places(theater, limit=5):
    """Local-layout fixtures used only when DEBUG and explicitly requested."""
    samples = [
        ('路地裏ビストロ', 'ビストロ', 2),
        ('下北酒場', '居酒屋', 3),
        ('夜更けの喫茶室', 'カフェ', 4),
        ('駅前餃子房', '中華料理', 4),
        ('茶沢ワインスタンド', 'ワインバー', 5),
    ]
    results = []
    for index, (name, category, walk_minutes) in enumerate(samples[:limit], start=1):
        query = quote_plus(f'{name} {theater.name}')
        results.append({
            'id': f'google:preview-{theater.slug}-{index}',
            'slug': None,
            'name': name,
            'category': category,
            'description': '',
            'address': f'{theater.area_name}・Google Maps検索候補',
            'nearest_station': '',
            'distance_note': f'{theater.name}から徒歩{walk_minutes}分',
            'benefit_text': '',
            'image_src': None,
            'google_map_url': f'https://www.google.com/maps/search/?api=1&query={query}',
            'after_viewing_count': 0,
            'is_featured': False,
            'is_want_to_go': False,
            'source': 'google_places',
            'listing_tier': 'google',
            'is_preview': True,
        })
    return results
