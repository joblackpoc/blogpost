from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Post, Comment, Category, Tag
from security.validators import validate_no_sql_injection, validate_no_command_injection

class PostForm(forms.ModelForm):
    title = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}),
                           validators=[validate_no_sql_injection])
    content = forms.CharField(widget=CKEditor5Widget(config_name='default'))
    video_link = forms.URLField(required=False, widget=forms.URLInput(attrs={
        'class': 'form-control',
        'placeholder': 'Paste YouTube video URL (e.g., https://www.youtube.com/watch?v=...)'
    }))
    link_url = forms.URLField(required=False, widget=forms.URLInput(attrs={
        'class': 'form-control',
        'id': 'id_link_url',
        'placeholder': 'Paste any website link (Facebook, Twitter, news, etc.)'
    }))
    link_title = forms.CharField(required=False, max_length=500, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Optional: Override preview title'
    }))
    link_description = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 2,
        'placeholder': 'Optional: Override preview description'
    }))
    link_image = forms.URLField(required=False, widget=forms.URLInput(attrs={
        'class': 'form-control',
        'placeholder': 'Optional: Direct image URL for preview'
    }))

    # Tags field with custom input
    tags_input = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'tags-input',
        'placeholder': 'Add tags/hashtags (e.g., python, webdev, tutorial) - separate with commas',
        'data-role': 'tagsinput'
    }), help_text='Enter tags separated by commas. Example: python, django, webdev')

    # SEO Fields
    meta_description = forms.CharField(required=False, max_length=160, widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 2,
        'placeholder': 'SEO meta description (160 characters max)',
        'maxlength': '160'
    }))
    meta_keywords = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Keywords for SEO (comma-separated)'
    }))

    # Social Media SEO
    og_title = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Custom title for Facebook/Twitter sharing (optional)'
    }))
    og_description = forms.CharField(required=False, max_length=300, widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 2,
        'placeholder': 'Custom description for social media (optional)'
    }))
    og_image = forms.URLField(required=False, widget=forms.URLInput(attrs={
        'class': 'form-control',
        'placeholder': 'Custom image URL for social sharing (optional)'
    }))

    class Meta:
        model = Post
        fields = ['title', 'category', 'excerpt', 'content', 'featured_image', 'video_link',
                  'link_url', 'link_title', 'link_description', 'link_image',
                  'meta_description', 'meta_keywords', 'og_title', 'og_description', 'og_image',
                  'status']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'excerpt': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate tags_input field with existing tags
        if self.instance and self.instance.pk:
            self.fields['tags_input'].initial = ', '.join([tag.name for tag in self.instance.tags.all()])

    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            instance.save()

        # Handle tags
        tags_input = self.cleaned_data.get('tags_input', '')
        if tags_input:
            # Clear existing tags
            instance.tags.clear()

            # Create or get tags
            tag_names = [name.strip().lower().replace('#', '') for name in tags_input.split(',') if name.strip()]
            for tag_name in tag_names:
                if tag_name:  # Ensure not empty
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    instance.tags.add(tag)

        if commit:
            self.save_m2m()

        return instance

class CommentForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
                             validators=[validate_no_sql_injection])

    class Meta:
        model = Comment
        fields = ['content']

class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}),
                          validators=[validate_no_sql_injection])
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
                                 required=False)

    class Meta:
        model = Category
        fields = ['name', 'description']
