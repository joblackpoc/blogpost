import bleach
from django.utils.html import escape

def sanitize_html(html_content):
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'ul', 'ol', 'li', 'a', 'img']
    allowed_attrs = {'a': ['href', 'title'], 'img': ['src', 'alt']}
    return bleach.clean(html_content, tags=allowed_tags, attributes=allowed_attrs, strip=True)

def escape_user_input(user_input):
    return escape(str(user_input))
