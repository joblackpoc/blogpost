"""
Authentication forms with security validation
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from security.validators import validate_no_sql_injection, validate_no_command_injection
import logging

logger = logging.getLogger('security')


class SecureRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        validators=[validate_no_sql_injection, validate_no_command_injection]
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            logger.info(f'New user registered: {user.username}')
        return user


class SecureLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username', 'autofocus': True}),
        validators=[validate_no_sql_injection, validate_no_command_injection]
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )


class OTPVerificationForm(forms.Form):
    otp_token = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '000000',
            'autofocus': True,
            'pattern': '[0-9]{6}',
            'maxlength': '6'
        }),
        label='Enter 6-digit code'
    )

    def clean_otp_token(self):
        token = self.cleaned_data.get('otp_token')
        if not token.isdigit():
            raise forms.ValidationError('OTP must contain only numbers.')
        return token
