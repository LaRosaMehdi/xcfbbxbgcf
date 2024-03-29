from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import update_session_auth_hash

from users.models import User
from users.views.users import user_set_is_connected
from smtp.views.forms import TwoFactorForm
from smtp.views.smtp import smtp_aouth_validation, smtp_setting_validation

import hashlib, random

# Generate a 6-digit validation code
# ----------------------------------

def generate_validation_code():
    validation_code = ''.join(random.choices('0123456789', k=6))
    hashed_validation_code = hashlib.sha256(validation_code.encode()).hexdigest()
    return validation_code, hashed_validation_code

# TWO FACTOR AOUTH (42, register & login)
# ---------------------------------------

def twofactor_oauth_send(request, user):
    user.backend = f'{ModelBackend.__module__}.{ModelBackend.__qualname__}'
    validation_code, hashed_validation_code = generate_validation_code()
    user.validation_code = hashed_validation_code
    user.save()
    smtp_aouth_validation(user, validation_code)    
    request.session['user_id'] = user.id
    return redirect('twofactor')

def twofactor_oauth(request):
    if request.method == 'POST':
        form = TwoFactorForm(request.POST)
        if form.is_valid():
            validation_code = form.cleaned_data['validation_code']
            user_id = request.session.get('user_id')
            if user_id:
                user = User.objects.get(id=user_id)
                hashed_validation_code_entered = hashlib.sha256(validation_code.encode()).hexdigest()
                if user.validation_code == hashed_validation_code_entered:
                    user.validation_code = None
                    user.save()
                    user_set_is_connected(user)
                    user.backend = f'{ModelBackend.__module__}.{ModelBackend.__qualname__}'
                    login(request, user)
                    return redirect('home')
                else:
                    user_set_is_connected(user, False)
                    messages.error(request, "Invalid validation code", extra_tags='twofactor_oauth_tag')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}", extra_tags='twofactor_oauth_tag')
    else:
        messages.error(request, "Invalid request method", extra_tags='twofactor_oauth_tag')
    return redirect('twofactor')

# TWO FACTOR SETTINGS (password change)
# -------------------------------------

def twofactor_setting_send(request, user, new_password):
    user.backend = f'{ModelBackend.__module__}.{ModelBackend.__qualname__}'
    validation_code, hashed_validation_code = generate_validation_code()
    user.validation_code = hashed_validation_code
    user.save()
    smtp_setting_validation(user, validation_code)    
    request.session['user_id'] = user.id
    request.session['new_password'] = new_password  # Store hashed password in session
    redirect_url = reverse('twofactor') + '?context=password_change'
    return HttpResponseRedirect(redirect_url)

def twofactor_setting(request):
    if request.method == 'POST':
        form = TwoFactorForm(request.POST)
        if form.is_valid():
            validation_code = form.cleaned_data['validation_code']
            user_id = request.session.get('user_id')
            if user_id:
                user = User.objects.get(id=user_id)
                hashed_validation_code_entered = hashlib.sha256(validation_code.encode()).hexdigest()
                if user.validation_code == hashed_validation_code_entered:
                    user.validation_code = None
                    hashed_new_password = request.session.pop('new_password', None)
                    if hashed_new_password:
                        user.password = hashed_new_password
                        user.save()
                        update_session_auth_hash(request, user)
                        messages.success(request, 'Your password was successfully updated!', extra_tags='change_password_tag')
                        return redirect('settings')
                    else:
                        messages.error(request, "No new password found in session", extra_tags='twofactor_oauth_tag')
                else:
                    user_set_is_connected(user, False)
                    messages.error(request, "Invalid validation code", extra_tags='twofactor_oauth_tag')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}", extra_tags='twofactor_oauth_tag')
    else:
        messages.error(request, "Invalid request method", extra_tags='twofactor_oauth_tag')
    return redirect('twofactor')