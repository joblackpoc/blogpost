"""
Blog URL Configuration with Like functionality and CKEditor upload
"""

from django.urls import path
from . import views
from . import ckeditor_views

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('post/<slug:slug>/like/', views.post_like, name='post_like'),
    path('post/create/', views.post_create, name='post_create'),
    path('post/<slug:slug>/edit/', views.post_edit, name='post_edit'),
    path('post/<slug:slug>/delete/', views.post_delete, name='post_delete'),
    path('comment/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
    path('category/<slug:slug>/', views.category_posts, name='category_posts'),
    path('my-posts/', views.my_posts, name='my_posts'),
    path('liked-posts/', views.liked_posts, name='liked_posts'),
    
    # CKEditor upload endpoints
    path('ckeditor/upload/', ckeditor_views.ckeditor_upload, name='ckeditor_upload'),
    path('ckeditor/browse/', ckeditor_views.ckeditor_browse, name='ckeditor_browse'),
]
