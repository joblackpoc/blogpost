# SecureBlog - Enterprise-Grade Django Web Application

A production-ready Django 5+ blog application with comprehensive OWASP and NIST security features.

## 🔐 Security Features Implemented

### OWASP Top 10 Protection
1. ✅ Path Traversal & LFI/RFI Protection
2. ✅ Command Injection Prevention
3. ✅ XSS Protection (Reflected, Stored, DOM-based)
4. ✅ SQL Injection Prevention
5. ✅ Brute Force Protection
6. ✅ Unrestricted File Upload Protection
7. ✅ ORM Injection Protection
8. ✅ Template Injection Protection
9. ✅ CSRF Protection
10. ✅ Security Headers

## 🚀 Features

- Multi-Factor Authentication (MFA) with Google Authenticator
- Blog System with CKEditor 5
- Password Reset using Django built-in system
- Admin Honeypot to catch malicious actors
- Security Dashboard for monitoring
- Rate Limiting on critical endpoints
- Comprehensive Logging of security events
- Responsive Design with Bootstrap 5

## 📋 Installation

### 1. Extract and Setup

```bash
# Extract the ZIP file
unzip secureblog_complete_*.zip
cd secureblog_project

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env with your settings
```

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Create Sample Categories

```bash
python manage.py shell
```

```python
from blog.models import Category

categories = [
    {'name': 'Technology', 'description': 'Tech news and tutorials'},
    {'name': 'Security', 'description': 'Cybersecurity articles'},
    {'name': 'Programming', 'description': 'Coding tips and tricks'},
]

for cat in categories:
    Category.objects.get_or_create(name=cat['name'], defaults=cat)

print("Categories created!")
exit()
```

### 7. Run Server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

## 🔑 Important URLs

- Blog: http://127.0.0.1:8000/blog/
- Login: http://127.0.0.1:8000/accounts/login/
- Register: http://127.0.0.1:8000/accounts/register/
- Real Admin: http://127.0.0.1:8000/secure-admin-panel/
- Honeypot: http://127.0.0.1:8000/admin/
- Security Dashboard: http://127.0.0.1:8000/security/dashboard/

## 📱 MFA Setup

1. Log in to your account
2. Go to Profile → MFA Settings
3. Click "Enable MFA"
4. Scan QR code with Google Authenticator
5. Enter 6-digit code to verify

## 🧪 Testing Security

1. **Rate Limiting**: Try 5+ failed login attempts
2. **XSS**: Try `<script>alert('XSS')</script>` in comments
3. **SQL Injection**: Try `' OR '1'='1` in login
4. **File Upload**: Try uploading .exe as .jpg
5. **CSRF**: Submit form without token

## 🚀 Production Deployment

Update settings.py:
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
SECRET_KEY = 'new-secret-key'
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

Use PostgreSQL and collect static files:
```bash
python manage.py collectstatic
```

## 📊 Project Structure

```
secureblog_project/
├── accounts/           # Authentication & MFA
├── blog/              # Blog application
├── security/          # Security features
├── secureblog/        # Main settings
├── templates/         # HTML templates
├── static/            # Static files
├── media/             # Uploads
├── logs/              # Security logs
└── requirements.txt   # Dependencies
```

## 🔒 Security Best Practices

1. Always use HTTPS in production
2. Keep SECRET_KEY secret
3. Regular security updates
4. Enable MFA for all users
5. Monitor security logs
6. Regular backups
7. Strong passwords
8. Validate all inputs

## 📝 License

Educational purposes

## 👨‍💻 Created By

Senior Software Engineer - Django Security Expert

---

**Note**: This is a complete, production-ready application with enterprise-grade security!
