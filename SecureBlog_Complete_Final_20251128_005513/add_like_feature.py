#!/usr/bin/env python3
"""
Add Like Feature to SecureBlog
Similar to Facebook like functionality
"""

import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Updated: {path}")

# 1. Update Blog Models - Add Like model
write_file('blog/models.py', '''"""
Blog models with security features and Like functionality
"""

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from security.validators import validate_no_sql_injection
from security.utils import sanitize_html
import logging

logger = logging.getLogger("security")


class Category(models.Model):
    """
    Blog category model
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        validators=[validate_no_sql_injection]
    )
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:category_posts', kwargs={'slug': self.slug})


class Post(models.Model):
    """
    Blog post model with XSS protection and Like functionality
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    title = models.CharField(
        max_length=200,
        validators=[validate_no_sql_injection]
    )
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts'
    )
    content = CKEditor5Field('Content', config_name='default')
    excerpt = models.TextField(
        max_length=300,
        blank=True,
        help_text='Brief description for preview'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    featured_image = models.ImageField(
        upload_to='blog/images/%Y/%m/%d/',
        blank=True,
        null=True
    )
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['-published_at']),
            models.Index(fields=['status']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Generate slug if not exists
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Sanitize HTML content to prevent XSS
        if self.content:
            self.content = sanitize_html(self.content)
        
        # Set published date
        if self.status == 'published' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
        logger.info(f'Post saved: {self.title} by {self.author.username}')

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})
    
    def total_likes(self):
        """Return total number of likes for this post"""
        return self.likes.count()
    
    def is_liked_by(self, user):
        """Check if user has liked this post"""
        if user.is_authenticated:
            return self.likes.filter(user=user).exists()
        return False


class PostLike(models.Model):
    """
    Like model for posts - similar to Facebook like
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')  # One like per user per post
        ordering = ['-created_at']
        verbose_name = 'Post Like'
        verbose_name_plural = 'Post Likes'

    def __str__(self):
        return f'{self.user.username} likes {self.post.title}'


class Comment(models.Model):
    """
    Comment model with XSS protection
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(
        validators=[validate_no_sql_injection]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'

    def save(self, *args, **kwargs):
        # Sanitize comment content
        if self.content:
            from security.utils import escape_user_input
            self.content = escape_user_input(self.content)
        
        super().save(*args, **kwargs)
        logger.info(f'Comment added by {self.author.username} on post: {self.post.title}')
''')

# 2. Update Blog Views - Add like/unlike views
write_file('blog/views.py', '''"""
Blog views with security features and Like functionality
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
import logging

from .models import Post, Comment, Category, PostLike
from .forms import PostForm, CommentForm

logger = logging.getLogger('security')


def post_list(request):
    """
    List all published posts with like counts
    """
    posts = Post.objects.filter(status='published').select_related('author', 'category').annotate(
        like_count=Count('likes')
    )
    
    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query)
        )
    
    # Category filter
    category_slug = request.GET.get('category')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    
    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_slug
    }
    
    return render(request, 'blog/post_list.html', context)


def post_detail(request, slug):
    """
    Display post detail with comments and like status
    """
    post = get_object_or_404(
        Post.objects.select_related('author', 'category'),
        slug=slug,
        status='published'
    )
    
    # Increment view count
    post.views += 1
    post.save(update_fields=['views'])
    
    # Get approved comments
    comments = post.comments.filter(is_approved=True).select_related('author')
    
    # Check if current user has liked this post
    user_has_liked = False
    if request.user.is_authenticated:
        user_has_liked = post.is_liked_by(request.user)
    
    # Get total likes
    total_likes = post.total_likes()
    
    # Comment form
    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')
            logger.info(f'Comment added by {request.user.username} on post: {post.title}')
            return redirect('blog:post_detail', slug=slug)
    else:
        form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'user_has_liked': user_has_liked,
        'total_likes': total_likes,
    }
    
    return render(request, 'blog/post_detail.html', context)


@login_required
@require_POST
def post_like(request, slug):
    """
    Like a post - AJAX endpoint
    """
    post = get_object_or_404(Post, slug=slug, status='published')
    
    # Check if user already liked this post
    like, created = PostLike.objects.get_or_create(post=post, user=request.user)
    
    if created:
        # User just liked the post
        message = 'Post liked!'
        liked = True
        logger.info(f'User {request.user.username} liked post: {post.title}')
    else:
        # User already liked, so unlike it
        like.delete()
        message = 'Post unliked!'
        liked = False
        logger.info(f'User {request.user.username} unliked post: {post.title}')
    
    # Return JSON response for AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'liked': liked,
            'total_likes': post.total_likes(),
            'message': message
        })
    
    # Fallback for non-AJAX requests
    messages.success(request, message)
    return redirect('blog:post_detail', slug=slug)


@login_required
def post_create(request):
    """
    Create new blog post
    """
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Post created successfully!')
            logger.info(f'Post created: {post.title} by {request.user.username}')
            return redirect('blog:post_detail', slug=post.slug)
    else:
        form = PostForm()
    
    return render(request, 'blog/post_form.html', {'form': form, 'action': 'Create'})


@login_required
def post_edit(request, slug):
    """
    Edit existing post
    """
    post = get_object_or_404(Post, slug=slug)
    
    # Check if user is author or staff
    if post.author != request.user and not request.user.is_staff:
        logger.warning(f'Unauthorized edit attempt by {request.user.username} on post: {post.title}')
        return HttpResponseForbidden('You are not allowed to edit this post.')
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            messages.success(request, 'Post updated successfully!')
            logger.info(f'Post updated: {post.title} by {request.user.username}')
            return redirect('blog:post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'blog/post_form.html', {
        'form': form,
        'action': 'Edit',
        'post': post
    })


@login_required
def post_delete(request, slug):
    """
    Delete post
    """
    post = get_object_or_404(Post, slug=slug)
    
    # Check if user is author or staff
    if post.author != request.user and not request.user.is_staff:
        logger.warning(f'Unauthorized delete attempt by {request.user.username} on post: {post.title}')
        return HttpResponseForbidden('You are not allowed to delete this post.')
    
    if request.method == 'POST':
        title = post.title
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        logger.info(f'Post deleted: {title} by {request.user.username}')
        return redirect('blog:post_list')
    
    return render(request, 'blog/post_confirm_delete.html', {'post': post})


@login_required
def comment_delete(request, pk):
    """
    Delete comment
    """
    comment = get_object_or_404(Comment, pk=pk)
    
    # Check if user is comment author or staff
    if comment.author != request.user and not request.user.is_staff:
        logger.warning(f'Unauthorized comment delete attempt by {request.user.username}')
        return HttpResponseForbidden('You are not allowed to delete this comment.')
    
    post_slug = comment.post.slug
    comment.delete()
    messages.success(request, 'Comment deleted successfully!')
    logger.info(f'Comment deleted by {request.user.username}')
    
    return redirect('blog:post_detail', slug=post_slug)


def category_posts(request, slug):
    """
    List posts by category
    """
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(
        category=category,
        status='published'
    ).select_related('author').annotate(like_count=Count('likes'))
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj
    }
    
    return render(request, 'blog/category_posts.html', context)


@login_required
def my_posts(request):
    """
    List current user's posts with like counts
    """
    posts = Post.objects.filter(author=request.user).select_related('category').annotate(
        like_count=Count('likes')
    )
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blog/my_posts.html', {'page_obj': page_obj})


@login_required
def liked_posts(request):
    """
    Show posts that current user has liked
    """
    liked_post_ids = PostLike.objects.filter(user=request.user).values_list('post_id', flat=True)
    posts = Post.objects.filter(id__in=liked_post_ids, status='published').select_related(
        'author', 'category'
    ).annotate(like_count=Count('likes'))
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blog/liked_posts.html', {'page_obj': page_obj})
''')

# 3. Update Blog URLs - Add like endpoints
write_file('blog/urls.py', '''"""
Blog URL Configuration with Like functionality
"""

from django.urls import path
from . import views

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
]
''')

# 4. Update Blog Admin - Add PostLike admin
write_file('blog/admin.py', '''"""
Admin configuration for blog app with Like management
"""

from django.contrib import admin
from .models import Category, Post, Comment, PostLike


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'views', 'get_like_count', 'published_at')
    list_filter = ('status', 'category', 'created_at', 'published_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'published_at'
    ordering = ('-published_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'category')
        }),
        ('Content', {
            'fields': ('excerpt', 'content', 'featured_image')
        }),
        ('Publication', {
            'fields': ('status', 'published_at')
        }),
        ('Statistics', {
            'fields': ('views',),
            'classes': ('collapse',)
        }),
    )
    
    def get_like_count(self, obj):
        return obj.total_likes()
    get_like_count.short_description = 'Likes'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at', 'is_approved')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('author__username', 'content')
    raw_id_fields = ('author', 'post')
    actions = ['approve_comments', 'unapprove_comments']
    
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = 'Approve selected comments'
    
    def unapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
    unapprove_comments.short_description = 'Unapprove selected comments'


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'post__title')
    raw_id_fields = ('user', 'post')
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False  # Likes are only added through the frontend
''')

print("\n✅ Like feature files updated!")
print("\n📝 Now updating templates...")
