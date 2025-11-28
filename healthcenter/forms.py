from django import forms
from .models import ContactMessage, Service, Announcement, Location, TeamMember, Position, Activity
from security.validators import validate_no_sql_injection
from django_ckeditor_5.widgets import CKEditor5Widget


class ContactForm(forms.ModelForm):
    """Contact form with validation"""
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Full Name',
            'required': True
        }),
        validators=[validate_no_sql_injection]
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com',
            'required': True
        })
    )

    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number (optional)'
        })
    )

    subject = forms.ChoiceField(
        choices=ContactMessage.SUBJECT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        })
    )

    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Your message...',
            'required': True
        }),
        validators=[validate_no_sql_injection]
    )

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']

    def clean_email(self):
        """Validate email format"""
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
        return email

    def clean_phone(self):
        """Clean and validate phone number"""
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove common phone formatting characters
            phone = phone.replace('-', '').replace('(', '').replace(')', '').replace(' ', '')
        return phone


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Service Name'}),
            'description': CKEditor5Widget(attrs={'class': 'django_ckeditor_5'}, config_name='default'),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'FontAwesome icon'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'schedule': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Service Schedule'}),
            'details': CKEditor5Widget(attrs={'class': 'django_ckeditor_5'}, config_name='extends'),
            'requirements': CKEditor5Widget(attrs={'class': 'django_ckeditor_5'}, config_name='extends'),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'icon': 'FontAwesome icon class (e.g., fa-heartbeat)',
            'image': 'Upload an image for the service.',
            'schedule': 'Service availability schedule.',
        }


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Announcement Title'}),
            'content': CKEditor5Widget(attrs={'class': 'django_ckeditor_5'}, config_name='default'),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'published_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        help_texts = {
            'priority': 'Set the urgency of the announcement.',
            'image': 'Upload an image for the announcement.',
        }


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location Name'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'working_hours': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'latitude': 'Google Maps latitude coordinate.',
            'longitude': 'Google Maps longitude coordinate.',
        }


class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'custom_position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Custom Position'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'bio': CKEditor5Widget(attrs={'class': 'django_ckeditor_5'}, config_name='default'),
            'specialization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Specialization'}),
            'qualifications': CKEditor5Widget(attrs={'class': 'django_ckeditor_5'}, config_name='extends'),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'custom_position': 'Use this for positions not in the list.',
            'qualifications': 'Education and certifications.',
        }


class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = '__all__'
        widgets = {
            'name_th': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Position Name (Thai)'}),
            'name_en': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Position Name (English)'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'name_th': 'Position name in Thai.',
            'name_en': 'Position name in English.',
        }


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Activity Title'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'URL Slug (auto-generated)'}),
            'description': CKEditor5Widget(attrs={'class': 'django_ckeditor_5'}, config_name='default'),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'activity_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'activity_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 9:00 AM - 3:00 PM'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'custom_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Custom Location'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Person Name'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Phone Number'}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Leave empty for unlimited'}),
            'is_registration_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'slug': 'Leave blank to auto-generate from title.',
            'location': 'Select a location from the list or use custom location below.',
            'custom_location': 'Use this if location is not in the list.',
            'max_participants': 'Maximum number of participants (optional).',
        }
