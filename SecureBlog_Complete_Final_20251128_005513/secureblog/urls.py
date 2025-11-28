"""
Main URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

handler400 = 'security.views.handler400'
handler403 = 'security.views.handler403'
handler404 = 'security.views.handler404'
handler500 = 'security.views.handler500'

urlpatterns = [
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path('secure-admin-panel/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('blog/', include('blog.urls')),
    path('security/', include('security.urls')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('', RedirectView.as_view(url='/blog/', permanent=False)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
