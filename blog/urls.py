from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/create/', views.post_create, name='post_create'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('post/<slug:slug>/like/', views.post_like, name='post_like'),
    path('post/<slug:slug>/edit/', views.post_edit, name='post_edit'),
    path('post/<slug:slug>/delete/', views.post_delete, name='post_delete'),
    path('comment/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
    path('categories/', views.category_list, name='category_list'),
    path('category/create/', views.category_create, name='category_create'),
    path('category/<slug:slug>/', views.category_posts, name='category_posts'),
    path('category/<slug:slug>/edit/', views.category_edit, name='category_edit'),
    path('category/<slug:slug>/delete/', views.category_delete, name='category_delete'),
    path('my-posts/', views.my_posts, name='my_posts'),
    path('liked-posts/', views.liked_posts, name='liked_posts'),
]
