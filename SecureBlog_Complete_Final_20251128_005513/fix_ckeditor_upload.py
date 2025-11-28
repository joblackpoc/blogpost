#!/usr/bin/env python3
"""
Fix CKEditor 5 Image Upload Issue
Adds proper image upload support to CKEditor
"""

import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Updated: {path}")

print("\n" + "="*70)
print("🔧 FIXING CKEDITOR 5 IMAGE UPLOAD")
print("="*70 + "\n")

# 1. Update settings.py with correct CKEditor configuration
write_file('secureblog/settings.py', '''"""
Django 5+ Secure Blog Application Settings
OWASP & NIST Compliant Configuration
"""

from pathlib import Path
from decouple import config
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production-12345678901234567890')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'django_otp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',
    'django_ckeditor_5',
    'admin_honeypot',
    'rest_framework',
    
    # Local apps
    'accounts.apps.AccountsConfig',
    'blog.apps.BlogConfig',
    'security.apps.SecurityConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'csp.middleware.CSPMiddleware',
    'security.middleware.SecurityHeadersMiddleware',
    'security.middleware.RateLimitMiddleware',
]

ROOT_URLCONF = 'secureblog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'autoescape': True,
        },
    },
]

WSGI_APPLICATION = 'secureblog.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_AGE = 3600
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_USE_SESSIONS = True
CSRF_FAILURE_VIEW = 'security.views.csrf_failure'

CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "https://cdn.ckeditor.com", "https://cdn.jsdelivr.net")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://cdn.ckeditor.com", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com")
CSP_IMG_SRC = ("'self'", "data:", "https:", "blob:")  # Added blob: for image uploads
CSP_FONT_SRC = ("'self'", "https://cdn.ckeditor.com", "https://cdnjs.cloudflare.com")
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)
CSP_FORM_ACTION = ("'self'",)
CSP_BASE_URI = ("'self'",)

FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB for images
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_PERMISSIONS = 0o644
ALLOWED_UPLOAD_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.webp']

RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'security': {
            'handlers': ['file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# ==================== CKEDITOR 5 CONFIGURATION ====================

# Custom upload path for CKEditor images
CKEDITOR_5_UPLOAD_PATH = "uploads/ckeditor/"

# CKEditor 5 file storage
CKEDITOR_5_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# CKEditor 5 configurations
customColorPalette = [
    {'color': 'hsl(4, 90%, 58%)', 'label': 'Red'},
    {'color': 'hsl(340, 82%, 52%)', 'label': 'Pink'},
    {'color': 'hsl(291, 64%, 42%)', 'label': 'Purple'},
    {'color': 'hsl(262, 52%, 47%)', 'label': 'Deep Purple'},
    {'color': 'hsl(231, 48%, 48%)', 'label': 'Indigo'},
    {'color': 'hsl(207, 90%, 54%)', 'label': 'Blue'},
]

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': {
            'items': [
                'heading', '|',
                'bold', 'italic', 'link', 'underline', 'strikethrough', 'code', 'subscript', 'superscript', 'highlight', '|',
                'bulletedList', 'numberedList', 'todoList', '|',
                'blockQuote', 'imageUpload', '|',
                'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
                'insertTable', '|',
                'outdent', 'indent', '|',
                'undo', 'redo'
            ],
            'shouldNotGroupWhenFull': True
        },
        'image': {
            'toolbar': [
                'imageTextAlternative', '|',
                'imageStyle:alignLeft',
                'imageStyle:alignRight',
                'imageStyle:alignCenter',
                'imageStyle:side',  '|',
                'toggleImageCaption', 'imageStyle:inline', 'imageStyle:breakText', 'imageStyle:wrapText', '|',
                'resizeImage',
            ],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]
        },
        'table': {
            'contentToolbar': ['tableColumn', 'tableRow', 'mergeTableCells',
                             'tableProperties', 'tableCellProperties'],
        },
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
                {'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3'},
            ]
        },
        'list': {
            'properties': {
                'styles': True,
                'startIndex': True,
                'reversed': True,
            }
        },
        'link': {
            'decorators': {
                'addTargetToExternalLinks': True,
                'defaultProtocol': 'https://',
                'toggleDownloadable': {
                    'mode': 'manual',
                    'label': 'Downloadable',
                    'attributes': {
                        'download': 'file'
                    }
                }
            }
        },
        'htmlSupport': {
            'allow': [
                {'name': '/./', 'attributes': True, 'classes': True, 'styles': True}
            ]
        },
    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3', '|',
            'bulletedList', 'numberedList', '|',
            'blockQuote',
        ],
        'toolbar': {
            'items': [
                'heading', '|',
                'outdent', 'indent', '|',
                'bold', 'italic', 'link', 'underline', 'strikethrough', 'code', 'subscript', 'superscript', 'highlight', '|',
                'bulletedList', 'numberedList', 'todoList', '|',
                'blockQuote', 'imageUpload', '|',
                'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat', 'insertTable', '|',
                'undo', 'redo'
            ],
            'shouldNotGroupWhenFull': True
        },
        'image': {
            'toolbar': [
                'imageTextAlternative', '|',
                'imageStyle:alignLeft',
                'imageStyle:alignRight',
                'imageStyle:alignCenter',
                'imageStyle:side', '|',
                'toggleImageCaption', 'imageStyle:inline', 'imageStyle:breakText', 'imageStyle:wrapText', '|',
                'resizeImage',
            ],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]
        },
        'table': {
            'contentToolbar': ['tableColumn', 'tableRow', 'mergeTableCells',
                             'tableProperties', 'tableCellProperties'],
        },
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
                {'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3'},
            ]
        },
        'list': {
            'properties': {
                'styles': True,
                'startIndex': True,
                'reversed': True,
            }
        },
        'htmlSupport': {
            'allow': [
                {'name': '/./', 'attributes': True, 'classes': True, 'styles': True}
            ]
        },
    }
}

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'blog:post_list'
LOGOUT_REDIRECT_URL = 'accounts:login'

ADMIN_HONEYPOT_EMAIL_ADMINS = True

OTP_TOTP_ISSUER = 'SecureBlog'
OTP_LOGIN_URL = 'accounts:otp_login'

PASSWORD_RESET_TIMEOUT = 3600
''')

# 2. Create custom upload view
write_file('blog/ckeditor_views.py', '''"""
Custom CKEditor upload view with security
"""

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
import os
import uuid
from PIL import Image
import logging

logger = logging.getLogger('security')


@login_required
@require_POST
def ckeditor_upload(request):
    """
    Handle CKEditor image uploads with security validation
    """
    try:
        # Get uploaded file
        upload_file = request.FILES.get('upload')
        
        if not upload_file:
            return JsonResponse({
                'error': {'message': 'No file uploaded'}
            }, status=400)
        
        # Validate file size (10MB max)
        if upload_file.size > 10 * 1024 * 1024:
            return JsonResponse({
                'error': {'message': 'File too large. Maximum size is 10MB.'}
            }, status=400)
        
        # Validate file extension
        ext = os.path.splitext(upload_file.name)[1].lower()
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        
        if ext not in allowed_extensions:
            return JsonResponse({
                'error': {'message': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'}
            }, status=400)
        
        # Validate that it's actually an image
        try:
            img = Image.open(upload_file)
            img.verify()
            upload_file.seek(0)  # Reset file pointer after verify
        except Exception:
            return JsonResponse({
                'error': {'message': 'Invalid image file'}
            }, status=400)
        
        # Generate secure filename
        original_name = upload_file.name
        filename = f"{uuid.uuid4().hex}{ext}"
        
        # Create upload path
        upload_path = os.path.join(settings.CKEDITOR_5_UPLOAD_PATH, filename)
        
        # Save file
        saved_path = default_storage.save(upload_path, upload_file)
        
        # Get URL
        file_url = default_storage.url(saved_path)
        
        # Make URL absolute
        if not file_url.startswith('http'):
            file_url = request.build_absolute_uri(file_url)
        
        logger.info(f'CKEditor image uploaded: {filename} by {request.user.username}')
        
        # Return success response in CKEditor format
        return JsonResponse({
            'url': file_url,
            'uploaded': 1,
            'fileName': original_name
        })
        
    except Exception as e:
        logger.error(f'CKEditor upload error: {str(e)}')
        return JsonResponse({
            'error': {'message': 'Upload failed. Please try again.'}
        }, status=500)


@login_required
@require_POST  
def ckeditor_browse(request):
    """
    Browse uploaded images
    """
    try:
        upload_dir = os.path.join(settings.MEDIA_ROOT, settings.CKEDITOR_5_UPLOAD_PATH)
        
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        files = []
        for filename in os.listdir(upload_dir):
            file_path = os.path.join(settings.CKEDITOR_5_UPLOAD_PATH, filename)
            file_url = default_storage.url(file_path)
            
            if not file_url.startswith('http'):
                file_url = request.build_absolute_uri(file_url)
            
            files.append({
                'name': filename,
                'url': file_url
            })
        
        return JsonResponse({
            'files': files
        })
        
    except Exception as e:
        logger.error(f'CKEditor browse error: {str(e)}')
        return JsonResponse({
            'error': {'message': 'Failed to load images'}
        }, status=500)
''')

# 3. Update blog URLs to include upload endpoint
write_file('blog/urls.py', '''"""
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
''')

# 4. Update main URLs to include proper media serving
write_file('secureblog/urls.py', '''"""
Main URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

handler400 = 'security.views.handler400'
handler403 = 'security.views.handler403'
handler404 = 'security.views.handler404'
handler500 = 'security.views.handler500'

urlpatterns = [
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path('secure-admin-panel/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('blog/', include('blog.urls')),
    path('security/', include('security.urls')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('', RedirectView.as_view(url='/blog/', permanent=False)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
''')

# 5. Update post form template to use custom upload
write_file('templates/blog/post_form.html', '''{% extends 'base.html' %}

{% block title %}{{ action }} Post - SecureBlog{% endblock %}

{% block extra_css %}
<style>
    .ck-editor__editable {
        min-height: 400px;
    }
</style>
{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-10">
        <div class="card">
            <div class="card-body p-5">
                <h2 class="mb-4">
                    <i class="fas fa-edit"></i> {{ action }} Post
                </h2>
                
                <form method="post" enctype="multipart/form-data" id="post-form">
                    {% csrf_token %}
                    
                    <div class="mb-3">
                        <label for="{{ form.title.id_for_label }}" class="form-label">Title</label>
                        {{ form.title }}
                        {% if form.title.errors %}
                            <div class="text-danger">{{ form.title.errors }}</div>
                        {% endif %}
                    </div>
                    
                    <div class="mb-3">
                        <label for="{{ form.category.id_for_label }}" class="form-label">Category</label>
                        {{ form.category }}
                        {% if form.category.errors %}
                            <div class="text-danger">{{ form.category.errors }}</div>
                        {% endif %}
                    </div>
                    
                    <div class="mb-3">
                        <label for="{{ form.excerpt.id_for_label }}" class="form-label">Excerpt</label>
                        {{ form.excerpt }}
                        {% if form.excerpt.errors %}
                            <div class="text-danger">{{ form.excerpt.errors }}</div>
                        {% endif %}
                    </div>
                    
                    <div class="mb-3">
                        <label for="{{ form.content.id_for_label }}" class="form-label">Content</label>
                        {{ form.content }}
                        {% if form.content.errors %}
                            <div class="text-danger">{{ form.content.errors }}</div>
                        {% endif %}
                    </div>
                    
                    <div class="mb-3">
                        <label for="{{ form.featured_image.id_for_label }}" class="form-label">Featured Image</label>
                        {{ form.featured_image }}
                        {% if form.featured_image.errors %}
                            <div class="text-danger">{{ form.featured_image.errors }}</div>
                        {% endif %}
                    </div>
                    
                    <div class="mb-3">
                        <label for="{{ form.status.id_for_label }}" class="form-label">Status</label>
                        {{ form.status }}
                        {% if form.status.errors %}
                            <div class="text-danger">{{ form.status.errors }}</div>
                        {% endif %}
                    </div>
                    
                    <div class="btn-group">
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-save"></i> Save Post
                        </button>
                        <a href="{% url 'blog:post_list' %}" class="btn btn-secondary">
                            <i class="fas fa-times"></i> Cancel
                        </a>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="https://cdn.ckeditor.com/ckeditor5/40.0.0/super-build/ckeditor.js"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    CKEDITOR.ClassicEditor.create(document.querySelector('#id_content'), {
        toolbar: {
            items: [
                'heading', '|',
                'bold', 'italic', 'link', 'underline', 'strikethrough', '|',
                'bulletedList', 'numberedList', '|',
                'blockQuote', 'uploadImage', '|',
                'fontSize', 'fontColor', 'fontBackgroundColor', '|',
                'insertTable', '|',
                'undo', 'redo'
            ],
            shouldNotGroupWhenFull: true
        },
        image: {
            toolbar: [
                'imageTextAlternative', '|',
                'imageStyle:inline',
                'imageStyle:block',
                'imageStyle:side', '|',
                'toggleImageCaption', 'imageStyle:alignLeft', 'imageStyle:alignCenter', 'imageStyle:alignRight'
            ]
        },
        simpleUpload: {
            uploadUrl: '/blog/ckeditor/upload/',
            withCredentials: true,
            headers: {
                'X-CSRFToken': csrfToken
            }
        }
    }).then(editor => {
        window.editor = editor;
        console.log('CKEditor initialized with image upload support');
    }).catch(error => {
        console.error('CKEditor initialization error:', error);
    });
});
</script>
{% endblock %}
''')

print("\n✅ All CKEditor fixes applied!")
print("\n" + "="*70)
print("📝 IMPORTANT: Next Steps")
print("="*70)
print("\n1. Install Pillow for image processing:")
print("   pip install Pillow")
print("\n2. Create upload directory:")
print("   mkdir -p media/uploads/ckeditor")
print("\n3. Restart your Django server")
print("\n4. Test image upload in CKEditor!")
print("\n" + "="*70)
