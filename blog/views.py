from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
import logging
from .models import Post, Comment, Category, PostLike, Tag
from .forms import PostForm, CommentForm, CategoryForm
from .utils import fetch_link_preview

logger = logging.getLogger('security')

def post_list(request):
    posts = Post.objects.filter(status='published').select_related('author', 'category').annotate(like_count=Count('likes'))
    search_query = request.GET.get('q', '')
    if search_query:
        posts = posts.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))

    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    categories = Category.objects.all()

    return render(request, 'blog/post_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query
    })

def post_detail(request, slug):
    post = get_object_or_404(Post.objects.select_related('author', 'category'), slug=slug, status='published')
    post.views += 1
    post.save(update_fields=['views'])
    comments = post.comments.filter(is_approved=True).select_related('author')

    user_has_liked = False
    if request.user.is_authenticated:
        user_has_liked = post.is_liked_by(request.user)

    total_likes = post.total_likes()

    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment added!')
            return redirect('blog:post_detail', slug=slug)
    else:
        form = CommentForm()

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
        'user_has_liked': user_has_liked,
        'total_likes': total_likes
    })

@login_required
@require_POST
def fetch_link_preview_api(request):
    """API endpoint to fetch link preview metadata"""
    url = request.POST.get('url', '').strip()

    if not url:
        return JsonResponse({'success': False, 'error': 'URL is required'}, status=400)

    metadata = fetch_link_preview(url)

    if metadata:
        return JsonResponse({
            'success': True,
            'data': metadata
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'Could not fetch link preview'
        }, status=400)

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user

            # Fetch link preview metadata if link_url is provided and fields are empty
            if post.link_url:
                # Only fetch if user hasn't manually provided metadata
                if not post.link_title and not post.link_description and not post.link_image:
                    metadata = fetch_link_preview(post.link_url)
                    if metadata:
                        post.link_title = metadata.get('title')
                        post.link_description = metadata.get('description')
                        post.link_image = metadata.get('image')
                        post.link_video = metadata.get('video')

            post.save()
            messages.success(request, 'Post created!')
            return redirect('blog:post_detail', slug=post.slug)
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form, 'action': 'Create'})

@login_required
def post_edit(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if post.author != request.user and not request.user.is_staff:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)

            # Fetch link preview metadata if link_url is provided and fields are empty
            if post.link_url:
                # Only fetch if user hasn't manually provided metadata
                if not post.link_title and not post.link_description and not post.link_image:
                    metadata = fetch_link_preview(post.link_url)
                    if metadata:
                        post.link_title = metadata.get('title')
                        post.link_description = metadata.get('description')
                        post.link_image = metadata.get('image')
                        post.link_video = metadata.get('video')

            post.save()
            messages.success(request, 'Post updated!')
            return redirect('blog:post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_form.html', {'form': form, 'action': 'Edit', 'post': post})

@login_required
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if post.author != request.user and not request.user.is_staff:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted!')
        return redirect('blog:post_list')
    return render(request, 'blog/post_confirm_delete.html', {'post': post})

@login_required
@require_POST
def post_like(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')

    like, created = PostLike.objects.get_or_create(post=post, user=request.user)

    if created:
        message = 'Post liked!'
        liked = True
        logger.info(f'User {request.user.username} liked post: {post.title}')
    else:
        like.delete()
        message = 'Post unliked!'
        liked = False
        logger.info(f'User {request.user.username} unliked post: {post.title}')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'liked': liked,
            'total_likes': post.total_likes(),
            'message': message
        })

    messages.success(request, message)
    return redirect('blog:post_detail', slug=slug)

@login_required
def my_posts(request):
    posts = Post.objects.filter(author=request.user).select_related('category').annotate(like_count=Count('likes'))
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'blog/my_posts.html', {'page_obj': page_obj})

@login_required
def liked_posts(request):
    liked_post_ids = PostLike.objects.filter(user=request.user).values_list('post_id', flat=True)
    posts = Post.objects.filter(id__in=liked_post_ids, status='published').select_related('author', 'category').annotate(like_count=Count('likes'))
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'blog/liked_posts.html', {'page_obj': page_obj})

@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.author != request.user and not request.user.is_staff:
        return HttpResponseForbidden()
    post_slug = comment.post.slug
    comment.delete()
    messages.success(request, 'Comment deleted!')
    return redirect('blog:post_detail', slug=post_slug)

def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category, status='published').select_related('author').annotate(like_count=Count('likes'))
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'blog/category_posts.html', {'category': category, 'page_obj': page_obj})

def tag_posts(request, slug):
    """View posts filtered by tag/hashtag"""
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.filter(tags=tag, status='published').select_related('author', 'category').annotate(like_count=Count('likes'))
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'blog/tag_posts.html', {'tag': tag, 'page_obj': page_obj})

@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'blog/category_list.html', {'categories': categories})

@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('blog:category_list')
    else:
        form = CategoryForm()
    return render(request, 'blog/category_form.html', {'form': form, 'action': 'Create'})

@login_required
def category_edit(request, slug):
    category = get_object_or_404(Category, slug=slug)
    if not request.user.is_staff:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('blog:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'blog/category_form.html', {'form': form, 'action': 'Edit', 'category': category})

@login_required
def category_delete(request, slug):
    category = get_object_or_404(Category, slug=slug)
    if not request.user.is_staff:
        return HttpResponseForbidden()

    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('blog:category_list')
    return render(request, 'blog/category_confirm_delete.html', {'category': category})
