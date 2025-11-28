from django.http import HttpResponseForbidden
from django.core.cache import cache
from django.conf import settings
import logging
import re

logger = logging.getLogger('security')

class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        if 'Server' in response:
            del response['Server']
        return response

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not getattr(settings, 'RATELIMIT_ENABLE', True):
            return self.get_response(request)
        
        ip = self.get_client_ip(request)
        if request.path.startswith('/accounts/login/') and request.method == 'POST':
            key = f'login_attempts_{ip}'
            attempts = cache.get(key, 0)
            if attempts >= 5:
                logger.warning(f'Rate limit: {ip}')
                return HttpResponseForbidden('Too many attempts')
            cache.set(key, attempts + 1, 300)
        return self.get_response(request)

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
