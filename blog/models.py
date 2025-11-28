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
    name = models.CharField(max_length=100, unique=True, validators=[validate_no_sql_injection])
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:category_posts", kwargs={"slug": self.slug})


class Tag(models.Model):
    """Tag/Hashtag model for SEO and content organization"""
    name = models.CharField(max_length=50, unique=True, validators=[validate_no_sql_injection])
    slug = models.SlugField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"#{self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        # Ensure tag name doesn't have spaces or special chars
        self.name = self.name.lower().replace(" ", "").replace("#", "")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:tag_posts", kwargs={"slug": self.slug})

    def post_count(self):
        return self.posts.filter(status='published').count()

class Post(models.Model):
    STATUS_CHOICES = [("draft", "Draft"), ("published", "Published")]
    title = models.CharField(max_length=200, validators=[validate_no_sql_injection])
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts")
    content = CKEditor5Field("Content", config_name="default")
    excerpt = models.TextField(max_length=300, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")
    featured_image = models.ImageField(upload_to="blog/images/%Y/%m/%d/", blank=True, null=True)
    video_link = models.URLField(max_length=500, blank=True, null=True, help_text="YouTube video URL")

    # Link preview fields
    link_url = models.URLField(max_length=1000, blank=True, null=True, help_text="Share a link (any website)")
    link_title = models.CharField(max_length=500, blank=True, null=True)
    link_description = models.TextField(blank=True, null=True)
    link_image = models.URLField(max_length=1000, blank=True, null=True)
    link_video = models.URLField(max_length=1000, blank=True, null=True)

    # SEO and Tags
    tags = models.ManyToManyField(Tag, related_name="posts", blank=True)
    meta_description = models.TextField(max_length=160, blank=True, help_text="SEO meta description (160 chars max)")
    meta_keywords = models.CharField(max_length=255, blank=True, help_text="Comma-separated keywords for SEO")

    # Social Media SEO (Open Graph)
    og_title = models.CharField(max_length=200, blank=True, help_text="Custom title for social media sharing")
    og_description = models.TextField(max_length=300, blank=True, help_text="Custom description for social media")
    og_image = models.URLField(max_length=500, blank=True, help_text="Custom image URL for social sharing")

    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.content:
            self.content = sanitize_html(self.content)
        if self.status == "published" and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:post_detail", kwargs={"slug": self.slug})

    def total_likes(self):
        return self.likes.count()

    def is_liked_by(self, user):
        if user.is_authenticated:
            return self.likes.filter(user=user).exists()
        return False

    def get_youtube_embed_url(self):
        """Extract YouTube video ID and return embed URL"""
        if not self.video_link:
            return None

        import re
        # Match various YouTube URL formats
        patterns = [
            r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})',
            r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]{11})',
            r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
        ]

        for pattern in patterns:
            match = re.search(pattern, self.video_link)
            if match:
                video_id = match.group(1)
                return f"https://www.youtube.com/embed/{video_id}"

        return None

    def get_meta_description(self):
        """Get meta description for SEO, fallback to excerpt or truncated content"""
        if self.meta_description:
            return self.meta_description
        elif self.excerpt:
            return self.excerpt[:160]
        else:
            # Strip HTML tags from content
            import re
            clean_content = re.sub('<[^<]+?>', '', self.content)
            return clean_content[:160]

    def get_og_title(self):
        """Get Open Graph title, fallback to post title"""
        return self.og_title if self.og_title else self.title

    def get_og_description(self):
        """Get Open Graph description, fallback to meta description"""
        return self.og_description if self.og_description else self.get_meta_description()

    def get_og_image(self):
        """Get Open Graph image, fallback to featured image or link image"""
        if self.og_image:
            return self.og_image
        elif self.featured_image:
            return self.featured_image.url
        elif self.link_image:
            return self.link_image
        return None

    def get_hashtags(self):
        """Return tags as hashtags string for display"""
        return " ".join([f"#{tag.name}" for tag in self.tags.all()])

class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "user")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} likes {self.post.title}"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField(validators=[validate_no_sql_injection])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"
