# 🚀 SecureBlog - Quick Start Guide

## One-Line Setup (After Extraction)

```bash
cd secureblog_project && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python manage.py migrate && python manage.py createsuperuser && python manage.py runserver
```

## Step-by-Step (5 Minutes)

### 1️⃣ Extract & Navigate
```bash
unzip secureblog_complete_*.zip
cd secureblog_project
```

### 2️⃣ Create Virtual Environment
```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Setup Database
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5️⃣ Run Server
```bash
python manage.py runserver
```

**Visit: http://127.0.0.1:8000/**

## 🎯 First Actions

1. **Create Your Profile**
   - Register at: /accounts/register/
   - Enable MFA: /accounts/mfa-setup/

2. **Create Categories**
```python
python manage.py shell
```
```python
from blog.models import Category
Category.objects.create(name='Technology', description='Tech news')
Category.objects.create(name='Security', description='Security articles')
exit()
```

3. **Create Your First Post**
   - Login
   - Click "New Post"
   - Write and publish!

## 🔑 Important URLs

| Feature | URL |
|---------|-----|
| Home | http://127.0.0.1:8000/ |
| Blog | http://127.0.0.1:8000/blog/ |
| Login | http://127.0.0.1:8000/accounts/login/ |
| Register | http://127.0.0.1:8000/accounts/register/ |
| Admin (Real) | http://127.0.0.1:8000/secure-admin-panel/ |
| Admin (Honeypot) | http://127.0.0.1:8000/admin/ |
| Security Dashboard | http://127.0.0.1:8000/security/dashboard/ |

## 🔐 Security Tests

### Test 1: Rate Limiting
Try logging in with wrong password 5+ times → Should be blocked

### Test 2: XSS Protection
Post comment with `<script>alert('XSS')</script>` → Should be sanitized

### Test 3: SQL Injection
Try username `' OR '1'='1` → Should be blocked

### Test 4: MFA
1. Profile → MFA Settings
2. Scan QR with Google Authenticator
3. Test login with 6-digit code

## 📦 What's Included

✅ **Django 5+** - Latest framework
✅ **MFA** - Google Authenticator
✅ **Blog** - CKEditor 5 integration
✅ **Security** - OWASP Top 10 protection
✅ **Admin Honeypot** - Catch attackers
✅ **Rate Limiting** - Brute force protection
✅ **Password Reset** - Built-in Django system
✅ **Responsive UI** - Bootstrap 5

## 🛠️ Project Structure

```
secureblog_project/
├── accounts/          # Auth & MFA
├── blog/             # Blog app
├── security/         # Security features
├── templates/        # HTML files
├── static/           # CSS, JS, images
├── media/            # Uploads
└── logs/             # Security logs
```

## ⚡ Quick Commands

```bash
# Create superuser
python manage.py createsuperuser

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Create admin user via shell
python manage.py shell
from django.contrib.auth.models import User
User.objects.create_superuser('admin', 'admin@example.com', 'SecurePass123!')
exit()
```

## 🎓 Learning Path

1. ✅ Install and run (5 min)
2. ✅ Create posts and comments (10 min)
3. ✅ Test security features (15 min)
4. ✅ Setup MFA (5 min)
5. ✅ Customize templates (30 min)
6. ✅ Deploy to production (varies)

## 📚 Documentation

- **Full Guide**: INSTALLATION_GUIDE.md
- **README**: README.md
- **Security Features**: Check templates/security/

## 🆘 Troubleshooting

### Error: Module not found
```bash
pip install -r requirements.txt --force-reinstall
```

### Error: Migration issues
```bash
python manage.py migrate --run-syncdb
```

### Error: Permission denied
```bash
chmod +x manage.py
```

## 🎉 You're Ready!

Your complete, production-ready Django application is now running!

**Features Ready to Use:**
- ✅ User registration & login
- ✅ Multi-factor authentication
- ✅ Blog with rich text editor
- ✅ Comments system
- ✅ Category management
- ✅ Security dashboard
- ✅ Admin panel (honeypot + real)
- ✅ Password reset via email
- ✅ Responsive design

**Happy Coding! 🚀**
