"""
Authentication views with MFA support
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.cache import cache
from django_otp import user_has_device
from django_otp.plugins.otp_totp.models import TOTPDevice
import qrcode
from io import BytesIO
import base64
import logging

from .forms import SecureRegistrationForm, SecureLoginForm, OTPVerificationForm
from .models import UserProfile, LoginAttempt

logger = logging.getLogger('security')


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def register_view(request):
    if request.user.is_authenticated:
        return redirect('blog:post_list')

    if request.method == 'POST':
        form = SecureRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            messages.success(request, 'Registration successful! Please log in.')
            logger.info(f'User registered successfully: {user.username}')
            return redirect('accounts:login')
    else:
        form = SecureRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('blog:post_list')

    ip_address = get_client_ip(request)
    cache_key = f'login_attempts_{ip_address}'

    if request.method == 'POST':
        form = SecureLoginForm(request, data=request.POST)
        
        attempts = cache.get(cache_key, 0)
        if attempts >= 5:
            messages.error(request, 'Too many login attempts. Please try again in 5 minutes.')
            logger.warning(f'Rate limit exceeded for IP: {ip_address}')
            return render(request, 'accounts/login.html', {'form': form})

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                LoginAttempt.objects.create(
                    username=username,
                    ip_address=ip_address,
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    success=True
                )

                profile = UserProfile.objects.get_or_create(user=user)[0]
                
                if profile.mfa_enabled or user_has_device(user):
                    request.session['pre_otp_user_id'] = user.id
                    return redirect('accounts:otp_verify')
                else:
                    login(request, user)
                    cache.delete(cache_key)
                    messages.success(request, f'Welcome back, {user.username}!')
                    logger.info(f'User logged in: {user.username}')
                    return redirect('blog:post_list')
            else:
                LoginAttempt.objects.create(
                    username=username,
                    ip_address=ip_address,
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    success=False
                )
                
                cache.set(cache_key, attempts + 1, 300)
                messages.error(request, 'Invalid username or password.')
                logger.warning(f'Failed login attempt for: {username} from {ip_address}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SecureLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def otp_verify_view(request):
    user_id = request.session.get('pre_otp_user_id')
    if not user_id:
        return redirect('accounts:login')

    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('accounts:login')

    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp_token = form.cleaned_data.get('otp_token')
            
            device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
            if device and device.verify_token(otp_token):
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                del request.session['pre_otp_user_id']
                messages.success(request, f'Welcome back, {user.username}!')
                logger.info(f'User logged in with MFA: {user.username}')
                return redirect('blog:post_list')
            else:
                messages.error(request, 'Invalid OTP code. Please try again.')
                logger.warning(f'Invalid OTP attempt for user: {user.username}')
    else:
        form = OTPVerificationForm()

    return render(request, 'accounts/otp_verify.html', {'form': form})


@login_required
def mfa_setup_view(request):
    user = request.user
    device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
    
    if request.method == 'POST':
        if 'enable_mfa' in request.POST:
            if not device:
                device = TOTPDevice.objects.create(user=user, name='default', confirmed=False)
            
            otpauth_url = device.config_url
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(otpauth_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return render(request, 'accounts/mfa_setup.html', {
                'qr_code': img_str,
                'secret_key': device.key,
                'device': device
            })
        
        elif 'confirm_mfa' in request.POST:
            otp_token = request.POST.get('otp_token')
            device = TOTPDevice.objects.filter(user=user, confirmed=False).first()
            
            if device and device.verify_token(otp_token):
                device.confirmed = True
                device.save()
                
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.mfa_enabled = True
                profile.save()
                
                messages.success(request, 'MFA enabled successfully!')
                logger.info(f'MFA enabled for user: {user.username}')
                return redirect('accounts:profile')
            else:
                messages.error(request, 'Invalid OTP code. Please try again.')
        
        elif 'disable_mfa' in request.POST:
            TOTPDevice.objects.filter(user=user).delete()
            profile = UserProfile.objects.get(user=user)
            profile.mfa_enabled = False
            profile.save()
            
            messages.success(request, 'MFA disabled successfully!')
            logger.info(f'MFA disabled for user: {user.username}')
            return redirect('accounts:profile')

    return render(request, 'accounts/mfa_setup.html', {'mfa_enabled': device is not None})


@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    context = {'profile': profile, 'mfa_enabled': profile.mfa_enabled}
    return render(request, 'accounts/profile.html', context)


@login_required
def logout_view(request):
    username = request.user.username
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    logger.info(f'User logged out: {username}')
    return redirect('accounts:login')
