from django.urls import path
from . import views
from .views import (
    ServiceListView, ServiceDetailView, ServiceCreateView, ServiceUpdateView, ServiceDeleteView,
    AnnouncementListView, AnnouncementDetailView, AnnouncementCreateView, AnnouncementUpdateView, AnnouncementDeleteView,
    LocationListView, LocationDetailView, LocationCreateView, LocationUpdateView, LocationDeleteView,
    TeamMemberListView, TeamMemberDetailView, TeamMemberCreateView, TeamMemberUpdateView, TeamMemberDeleteView,
    PositionListView, PositionDetailView, PositionCreateView, PositionUpdateView, PositionDeleteView,
    ActivityListView, ActivityDetailView, ActivityCreateView, ActivityUpdateView, ActivityDeleteView
)

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
    path('dashboard/', views.dashboard, name='dashboard'),

    # Service CRUD
    path('service/list/', ServiceListView.as_view(), name='service_list'),
    path('service/create/', ServiceCreateView.as_view(), name='service_create'),
    path('service/<int:pk>/', ServiceDetailView.as_view(), name='service_detail_cbv'),
    path('service/<int:pk>/update/', ServiceUpdateView.as_view(), name='service_update'),
    path('service/<int:pk>/delete/', ServiceDeleteView.as_view(), name='service_delete'),

    # Announcement CRUD
    path('announcement/list/', AnnouncementListView.as_view(), name='announcement_list'),
    path('announcement/create/', AnnouncementCreateView.as_view(), name='announcement_create'),
    path('announcement/<int:pk>/', AnnouncementDetailView.as_view(), name='announcement_detail_cbv'),
    path('announcement/<int:pk>/update/', AnnouncementUpdateView.as_view(), name='announcement_update'),
    path('announcement/<int:pk>/delete/', AnnouncementDeleteView.as_view(), name='announcement_delete'),

    # Location CRUD
    path('location/list/', LocationListView.as_view(), name='location_list'),
    path('location/create/', LocationCreateView.as_view(), name='location_create'),
    path('location/<int:pk>/', LocationDetailView.as_view(), name='location_detail'),
    path('location/<int:pk>/update/', LocationUpdateView.as_view(), name='location_update'),
    path('location/<int:pk>/delete/', LocationDeleteView.as_view(), name='location_delete'),

    # TeamMember CRUD
    path('teammember/list/', TeamMemberListView.as_view(), name='teammember_list'),
    path('teammember/create/', TeamMemberCreateView.as_view(), name='teammember_create'),
    path('teammember/<int:pk>/', TeamMemberDetailView.as_view(), name='teammember_detail'),
    path('teammember/<int:pk>/update/', TeamMemberUpdateView.as_view(), name='teammember_update'),
    path('teammember/<int:pk>/delete/', TeamMemberDeleteView.as_view(), name='teammember_delete'),

    # Position CRUD
    path('position/list/', PositionListView.as_view(), name='position_list'),
    path('position/create/', PositionCreateView.as_view(), name='position_create'),
    path('position/<int:pk>/', PositionDetailView.as_view(), name='position_detail'),
    path('position/<int:pk>/update/', PositionUpdateView.as_view(), name='position_update'),
    path('position/<int:pk>/delete/', PositionDeleteView.as_view(), name='position_delete'),

    # Activity CRUD
    path('activity/list/', ActivityListView.as_view(), name='activity_list'),
    path('activity/create/', ActivityCreateView.as_view(), name='activity_create'),
    path('activity/<slug:slug>/', ActivityDetailView.as_view(), name='activity_detail'),
    path('activity/<int:pk>/update/', ActivityUpdateView.as_view(), name='activity_update'),
    path('activity/<int:pk>/delete/', ActivityDeleteView.as_view(), name='activity_delete'),
]
