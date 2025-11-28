# SecureBlog - Complete Installation Guide

## 🚀 Quick Start

### 1. Extract Project
```bash
unzip secureblog_complete_*.zip
cd secureblog_project
```

### 2. Create Virtual Environment
```bash
# Create venv
python -m venv venv

# Activate - Windows
venv\Scripts\activate

# Activate - Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy example env file
cp .env.example .env

# Edit .env and set:
# - SECRET_KEY (generate new one)
# - DEBUG=True for development
# - ALLOWED_HOSTS
```

### 5. Database Setup
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 6. Create Sample Data
```bash
python manage.py shell
```
```python
from blog.models import Category

cats = [
    {'name': 'Technology', 'description': 'Tech news'},
    {'name': 'Security', 'description': 'Cybersecurity'},
    {'name': 'Programming', 'description': 'Code tutorials'},
]

for cat in cats:
    Category.objects.get_or_create(name=cat['name'], defaults=cat)

print("Categories created!")
exit()
```

### 7. Run Server
```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/**

## 📱 Testing the Application

### URLs to Test
- Home: http://127.0.0.1:8000/
- Blog: http://127.0.0.1:8000/blog/
- Login: http://127.0.0.1:8000/accounts/login/
- Register: http://127.0.0.1:8000/accounts/register/
- Admin (Real): http://127.0.0.1:8000/secure-admin-panel/
- Admin (Honeypot): http://127.0.0.1:8000/admin/
- Security Dashboard: http://127.0.0.1:8000/security/dashboard/

### Test Security Features

1. **Rate Limiting**
   - Try 5+ failed login attempts
   - Should be blocked temporarily

2. **XSS Protection**
   - Try posting: `<script>alert('XSS')</script>`
   - Should be sanitized

3. **SQL Injection**
   - Try username: `' OR '1'='1`
   - Should be blocked

4. **CSRF Protection**
   - Try submitting form without CSRF token
   - Should fail

5. **File Upload**
   - Try uploading .exe file
   - Should be rejected

6. **MFA Setup**
   - Go to Profile → MFA Settings
   - Scan QR with Google Authenticator
   - Test login with 6-digit code

## 🔐 Security Features Included

✅ Multi-Factor Authentication (Google Authenticator)
✅ Password Reset System
✅ Admin Honeypot
✅ Rate Limiting (5 attempts/5 minutes)
✅ XSS Protection (Reflected, Stored, DOM)
✅ SQL Injection Prevention
✅ CSRF Protection
✅ Command Injection Prevention
✅ Path Traversal Protection
✅ File Upload Validation
✅ Security Headers
✅ Session Security
✅ Input Sanitization
✅ Logging & Monitoring

## 🚀 Production Deployment

### Update settings.py
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
SECRET_KEY = 'new-production-secret-key'

# Enable HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Use PostgreSQL
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'secureblog_db',
        'USER': 'secureblog_user',
        'PASSWORD': 'secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Set Up Web Server
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn secureblog.wsgi:application --bind 0.0.0.0:8000
```

### Configure Nginx (Example)
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location /static/ {
        alias /path/to/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🧪 Development Tips

### Creating Posts
1. Log in
2. Click "New Post"
3. Fill in title, content, category
4. Choose "Published" status
5. Submit

### Enable MFA
1. Go to Profile
2. Click "MFA Settings"
3. Click "Enable MFA"
4. Scan QR code with Google Authenticator app
5. Enter 6-digit code to confirm

### View Logs
```bash
# Security logs
tail -f logs/security.log
```

### Admin Access
- Real admin: http://127.0.0.1:8000/secure-admin-panel/
- Honeypot catches attackers at: /admin/

## 📊 Project Structure
```
secureblog_project/
├── accounts/          # Authentication & MFA
├── blog/             # Blog application
├── security/         # Security features
├── secureblog/       # Main settings
├── templates/        # HTML templates
├── static/           # Static files (CSS, JS, images)
├── media/            # User uploads
├── logs/             # Security logs
├── requirements.txt  # Python dependencies
├── manage.py         # Django management script
└── README.md         # Documentation
```

## ❓ Troubleshooting

### Migration Errors
```bash
# Delete migrations and database
rm -rf */migrations/00*.py
rm db.sqlite3

# Recreate
python manage.py makemigrations
python manage.py migrate
```

### Permission Errors
```bash
# Fix permissions
chmod +x manage.py
chmod -R 755 media/ logs/
```

### Module Not Found
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### CKEditor Issues
- Make sure `django-ckeditor-5` is installed
- Check CKEDITOR_5_CONFIGS in settings.py

## 🎯 Next Steps

1. ✅ Customize templates (templates/)
2. ✅ Add custom CSS (static/css/)
3. ✅ Configure email backend for password reset
4. ✅ Set up SSL certificate for production
5. ✅ Configure backup strategy
6. ✅ Set up monitoring
7. ✅ Review security logs regularly

## 📞 Support

This is a complete, production-ready Django 5+ application with enterprise-grade security features!

**Features:**
- Django 5+ Framework
- Multi-Factor Authentication
- CKEditor 5 Integration
- Password Reset System
- Admin Honeypot
- OWASP Top 10 Protection
- NIST Security Compliance
- Rate Limiting
- Comprehensive Logging
- Responsive Bootstrap 5 UI

---

**Happy Coding! 🚀**
