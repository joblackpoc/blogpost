from django.contrib import admin
from .models import Category, Post, Comment, PostLike

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'views', 'get_like_count', 'published_at')
    list_filter = ('status', 'category', 'created_at')
    prepopulated_fields = {'slug': ('title',)}

    def get_like_count(self, obj):
        return obj.total_likes()
    get_like_count.short_description = 'Likes'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at', 'is_approved')
    list_filter = ('is_approved', 'created_at')

@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'post__title')
    raw_id_fields = ('user', 'post')
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False
