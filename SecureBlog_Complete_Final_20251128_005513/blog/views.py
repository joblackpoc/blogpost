"""
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
