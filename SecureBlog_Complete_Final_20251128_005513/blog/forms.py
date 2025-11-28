from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Post, Comment, Category
from security.validators import validate_no_sql_injection, validate_no_command_injection

class PostForm(forms.ModelForm):
    title = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}),
                           validators=[validate_no_sql_injection])
    content = forms.CharField(widget=CKEditor5Widget(config_name='default'))
    
    class Meta:
        model = Post
        fields = ['title', 'category', 'excerpt', 'content', 'featured_image', 'status']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'excerpt': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class CommentForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
                             validators=[validate_no_sql_injection])
    
    class Meta:
        model = Comment
        fields = ['content']
