import hashlib
import hmac
import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings


STRIPE_API_BASE = 'https://api.stripe.com/v1'


class StripeRequestError(Exception):
    pass


def stripe_request(path, data=None, method='POST'):
    encoded = urlencode(data or {}).encode('utf-8') if method != 'GET' else None
    request = Request(
        f'{STRIPE_API_BASE}{path}',
        data=encoded,
        method=method,
        headers={
            'Authorization': f'Bearer {settings.STRIPE_SECRET_KEY}',
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    )
    try:
        with urlopen(request, timeout=10) as response:
            return json.load(response)
    except HTTPError as error:
        try:
            detail = json.load(error).get('error', {}).get('message', '')
        except (ValueError, AttributeError):
            detail = ''
        raise StripeRequestError(detail or 'Stripeとの通信に失敗しました。') from error
    except (URLError, TimeoutError, ValueError) as error:
        raise StripeRequestError('Stripeとの通信に失敗しました。') from error


def verify_webhook_signature(payload, signature_header, tolerance=300):
    if not settings.STRIPE_WEBHOOK_SECRET or not signature_header:
        return False
    parts = {}
    signatures = []
    for item in signature_header.split(','):
        key, _, value = item.partition('=')
        if key == 'v1':
            signatures.append(value)
        else:
            parts[key] = value
    try:
        timestamp = int(parts['t'])
    except (KeyError, TypeError, ValueError):
        return False
    if abs(time.time() - timestamp) > tolerance:
        return False
    signed_payload = f'{timestamp}.'.encode('utf-8') + payload
    expected = hmac.new(
        settings.STRIPE_WEBHOOK_SECRET.encode('utf-8'),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()
    return any(hmac.compare_digest(expected, signature) for signature in signatures)
