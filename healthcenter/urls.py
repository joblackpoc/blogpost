from django.urls import path
from . import views

app_name = 'healthcenter'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about_us, name='about'),
    path('services/', views.services, name='services'),
    path('services/<slug:slug>/', views.service_detail, name='service_detail'),
    path('announcements/', views.announcements, name='announcements'),
    path('announcements/<slug:slug>/', views.announcement_detail, name='announcement_detail'),
    path('team/', views.team, name='team'),
    path('locations/', views.locations_view, name='locations'),
    path('contact/', views.contact, name='contact'),
]
