"""
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
