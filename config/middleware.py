from django.middleware.csrf import CsrfViewMiddleware
from django.conf import settings


class CapacitorCsrfMiddleware(CsrfViewMiddleware):
    """
    Capacitor/Ionic apps cannot access document.cookie, so the CSRF token
    sent via X-CSRFToken header is always empty. This middleware detects
    Capacitor requests (via X-Requested-With header) and skips CSRF
    validation entirely. Session authentication provides sufficient
    protection for native app requests.
    """

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'capacitor':
            return None
        return super().process_view(request, callback, callback_args, callback_kwargs)
