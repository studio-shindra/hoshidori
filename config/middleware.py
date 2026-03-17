from django.middleware.csrf import CsrfViewMiddleware
from django.conf import settings


class CapacitorCsrfMiddleware(CsrfViewMiddleware):
    """
    Capacitor/Ionic apps cannot send Referer headers, causing Django's
    CSRF Referer check to fail on HTTPS. This middleware detects requests
    from Capacitor (via X-Requested-With header) and injects a trusted
    Referer so Django's standard CSRF token validation still runs.
    """

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'capacitor':
            referer = request.META.get('HTTP_REFERER', '')
            if not referer:
                for origin in settings.CSRF_TRUSTED_ORIGINS:
                    if origin.startswith('https://'):
                        request.META['HTTP_REFERER'] = origin + '/'
                        break
        return super().process_view(request, callback, callback_args, callback_kwargs)
