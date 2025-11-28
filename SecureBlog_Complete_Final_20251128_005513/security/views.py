from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
import logging

logger = logging.getLogger('security')

def csrf_failure(request, reason=""):
    logger.warning(f'CSRF failure: {reason}')
    return render(request, 'security/csrf_failure.html', {'reason': reason}, status=403)

@staff_member_required
def security_dashboard(request):
    return render(request, 'security/dashboard.html', {
        'total_events_today': 0,
        'blocked_ips': [],
    })

def handler400(request, exception=None):
    return render(request, 'security/400.html', status=400)

def handler403(request, exception=None):
    return render(request, 'security/403.html', status=403)

def handler404(request, exception=None):
    return render(request, 'security/404.html', status=404)

def handler500(request):
    return render(request, 'security/500.html', status=500)
