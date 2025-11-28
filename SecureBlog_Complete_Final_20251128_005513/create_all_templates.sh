#!/bin/bash

# Base template
cat > templates/base.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}SecureBlog{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{% url 'blog:post_list' %}"><i class="fas fa-shield-alt"></i> SecureBlog</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="{% url 'blog:post_list' %}">Home</a></li>
                    {% if user.is_authenticated %}
                        <li class="nav-item"><a class="nav-link" href="{% url 'blog:post_create' %}">New Post</a></li>
                        <li class="nav-item"><a class="nav-link" href="{% url 'blog:my_posts' %}">My Posts</a></li>
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">{{ user.username }}</a>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item" href="{% url 'accounts:profile' %}">Profile</a></li>
                                <li><a class="dropdown-item" href="{% url 'accounts:mfa_setup' %}">MFA</a></li>
                                <li><hr class="dropdown-divider"></li>
                                <li><a class="dropdown-item" href="{% url 'accounts:logout' %}">Logout</a></li>
                            </ul>
                        </li>
                        {% if user.is_staff %}
                            <li class="nav-item"><a class="nav-link" href="{% url 'security:dashboard' %}">Security</a></li>
                        {% endif %}
                    {% else %}
                        <li class="nav-item"><a class="nav-link" href="{% url 'accounts:login' %}">Login</a></li>
                        <li class="nav-item"><a class="nav-link" href="{% url 'accounts:register' %}">Register</a></li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    {% if messages %}
        <div class="container mt-3">
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        </div>
    {% endif %}

    <div class="container my-4">
        {% block content %}{% endblock %}
    </div>

    <footer class="bg-dark text-white text-center py-3 mt-5">
        <p class="mb-0">&copy; 2024 SecureBlog - OWASP & NIST Compliant</p>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
EOF

# Login template
mkdir -p templates/accounts
cat > templates/accounts/login.html << 'EOF'
{% extends 'base.html' %}
{% block title %}Login - SecureBlog{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-5">
        <div class="card">
            <div class="card-body p-5">
                <h2 class="text-center mb-4"><i class="fas fa-sign-in-alt"></i> Login</h2>
                <form method="post">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label>Username</label>
                        {{ form.username }}
                        {% if form.username.errors %}<div class="text-danger">{{ form.username.errors }}</div>{% endif %}
                    </div>
                    <div class="mb-3">
                        <label>Password</label>
                        {{ form.password }}
                        {% if form.password.errors %}<div class="text-danger">{{ form.password.errors }}</div>{% endif %}
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Login</button>
                    <div class="text-center mt-3">
                        <a href="{% url 'accounts:password_reset' %}">Forgot Password?</a>
                    </div>
                    <hr>
                    <div class="text-center">
                        <p>Don't have an account? <a href="{% url 'accounts:register' %}">Register</a></p>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
EOF

# Register template
cat > templates/accounts/register.html << 'EOF'
{% extends 'base.html' %}
{% block title %}Register - SecureBlog{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-body p-5">
                <h2 class="text-center mb-4"><i class="fas fa-user-plus"></i> Register</h2>
                <form method="post">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label>Username</label>
                        {{ form.username }}
                        {% if form.username.errors %}<div class="text-danger">{{ form.username.errors }}</div>{% endif %}
                    </div>
                    <div class="mb-3">
                        <label>Email</label>
                        {{ form.email }}
                        {% if form.email.errors %}<div class="text-danger">{{ form.email.errors }}</div>{% endif %}
                    </div>
                    <div class="mb-3">
                        <label>Password</label>
                        {{ form.password1 }}
                        {% if form.password1.errors %}<div class="text-danger">{{ form.password1.errors }}</div>{% endif %}
                    </div>
                    <div class="mb-3">
                        <label>Confirm Password</label>
                        {{ form.password2 }}
                        {% if form.password2.errors %}<div class="text-danger">{{ form.password2.errors }}</div>{% endif %}
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Register</button>
                    <hr>
                    <div class="text-center">
                        <p>Already have account? <a href="{% url 'accounts:login' %}">Login</a></p>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
EOF

echo "✅ All templates created!"
