from django.contrib.sitemaps import Sitemap
from .models import Service, Announcement, Location


class ServiceSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Service.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at


class AnnouncementSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Announcement.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at


class LocationSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Location.objects.filter(is_active=True)
