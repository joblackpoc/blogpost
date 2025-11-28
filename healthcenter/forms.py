from django import forms
from .models import ContactMessage
from security.validators import validate_no_sql_injection


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
