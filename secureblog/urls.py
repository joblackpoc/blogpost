"""
Main URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.sitemaps.views import sitemap
from healthcenter.sitemaps import ServiceSitemap, AnnouncementSitemap, LocationSitemap

sitemaps = {
    'services': ServiceSitemap,
    'announcements': AnnouncementSitemap,
    'locations': LocationSitemap,
}

handler400 = 'security.views.handler400'
handler403 = 'security.views.handler403'
handler404 = 'security.views.handler404'
handler500 = 'security.views.handler500'

urlpatterns = [
    # path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),  # Commented out - incompatible with Django 5+
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('blog/', include('blog.urls')),
    path('security/', include('security.urls')),
    path('healthcenter/', include('healthcenter.urls')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('', include('healthcenter.urls')),  # Redirect root to healthcenter app
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
