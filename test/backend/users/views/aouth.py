import requests, re, logging
from requests import get
from users.models import User
from django.urls import reverse
from django.conf import settings
from django.db import IntegrityError
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth.backends import ModelBackend

from users.views import *
from users.views.users import user_set_is_connected
from smtp.views.twofactor import twofactor_oauth_send

logger = logging.getLogger(__name__)

# AOUTHENTIFICATION
# -----------------

class AouthUser(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user_obj = User.objects.get(username=username)
            if user_obj.check_password(password):
                return user_obj
        except User.DoesNotExist:
            return None

# MIDDLWARE
# ---------

class AouthRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and not any(request.path.startswith(url) for url in settings.MIDDLEWARE_EXEMPT_URLS):
            unauthorized_url = request.path
            messages.warning(request, f"You need to log in to access this page. {unauthorized_url}", extra_tags="aouth_required_middleware_tag")
            return redirect('login')
        return self.get_response(request)

# LOGIN
# -----

def aouth_login_form(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data['user_id']
            password = form.cleaned_data['password']
            if '@' in user_id:
                user = authenticate(request, email=user_id, password=password)
            else:
                user = authenticate(request, username=user_id, password=password)
                
            if user is not None:
                return twofactor_oauth_send(request, user)
            else:
                messages.error(request, "Invalid username or password", extra_tags='aouth_login_tag')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}", extra_tags='aouth_login_tag')
    
    return redirect('login')


# REGISTRATION
# ------------

def aouth_register_form(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        
        if form.is_valid():
            try:
                user = form.save()
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                user = authenticate(request, username=username, password=password)      
                if user is not None:
                    return twofactor_oauth_send(request, user)
                else:
                    messages.error(request, "Failed to authenticate user after registration", extra_tags='aouth_register_tag')
            
            except IntegrityError as e:
                if 'username' in e.args[0]:  # Check if the error is related to the username field
                    messages.error(request, "Username already exists", extra_tags='aouth_register_tag')
                if 'email' in e.args[0]:  # Check if the error is related to the email field
                    messages.error(request, "Email already exists", extra_tags='aouth_register_tag')

        else:
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    messages.error(request, f"{field}: {error}", extra_tags='aouth_register_tag')
    return redirect('register')

# 42 OAUTH REGISTRATION
# ---------------------

def aouth_callback_register(request):
    logger.info("Authentication via 42 oauth")

    code = request.GET.get('code')
    if not code:
        logger.error("No code provided in request")
        messages.error(request, "Code not provided", extra_tags='aouth_callback_register')
        return redirect('register')

    try:
        token_response = requests.post('https://api.intra.42.fr/oauth/token', data={
            'grant_type': 'authorization_code',
            'client_id': settings.OAUTH_REGISTER_CLIENT_ID,
            'client_secret': settings.OAUTH_REGISTER_CLIENT_SECRET,
            'code': code,
            'redirect_uri': settings.OAUTH_REGISTER_REDIRECT_URI,
        })

        if token_response.status_code != 200:
            logger.error(f"Failed to fetch access token: {token_response.json()}")
            messages.error(request, "Failed to fetch access token", extra_tags='aouth_callback_register')
            return redirect('register')

        access_token = token_response.json().get('access_token')

        user_response = requests.get('https://api.intra.42.fr/v2/me', headers={
            'Authorization': f'Bearer {access_token}',
        })

        if user_response.status_code != 200:
            logger.error(f"Failed to fetch user information: {user_response.json()}")
            messages.error(request, "Failed to fetch user information", extra_tags='aouth_callback_register')
            return redirect('register')

        user_info = user_response.json()
        User = get_user_model()
        user_email = user_info['email']
        user = User.objects.filter(email=user_email).first()
        if user:
            user_set_is_connected(user, False)
            messages.error(request, "You are already registered.", extra_tags='aouth_callback_register')
            return redirect('register')

        user = User.objects.create_user(username=f"{user_info['login']}_42", email=user_email, image_url=user_info['image']['link'])
        return twofactor_oauth_send(request, user)

    except Exception as e:
        logger.exception("An error occurred in oauth_callback_register")
        messages.error(request, "An error occurred during registration", extra_tags='aouth_callback_register')
        return redirect('register')

# 42 OAUTH LOGIN
# --------------

def aouth_callback_login(request):
    logger.info("Authentication via 42 oauth")

    code = request.GET.get('code')
    if not code:
        logger.error("No code provided in request")
        messages.error(request, "Code not provided", extra_tags='aouth_callback_login')
        return redirect('login')

    try:
        token_response = requests.post('https://api.intra.42.fr/oauth/token', data={
            'grant_type': 'authorization_code',
            'client_id': settings.AOUTH_LOGIN_CLIENT_ID,
            'client_secret': settings.OAUTH_LOGIN_CLIENT_SECRET,
            'code': code,
            'redirect_uri': settings.AOUTH_LOGIN_REDIRECT_URI,
        })

        if token_response.status_code != 200:
            logger.error(f"Failed to fetch access token: {token_response.json()}")
            messages.error(request, "Failed to fetch access token", extra_tags='aouth_callback_login')
            return redirect('login')

        access_token = token_response.json().get('access_token')

        user_response = requests.get('https://api.intra.42.fr/v2/me', headers={
            'Authorization': f'Bearer {access_token}',
        })

        if user_response.status_code != 200:
            logger.error(f"Failed to fetch user information: {user_response.json()}")
            messages.error(request, "Failed to fetch user information", extra_tags='aouth_callback_login')
            return redirect('login')

        user_info = user_response.json()
        User = get_user_model()
        user_email = user_info['email']
        user = User.objects.filter(email=user_email).first()
        if not user:
            messages.error(request, "You are not registered. Please register first.", extra_tags='aouth_callback_login')
            return redirect('login')
        return twofactor_oauth_send(request, user)

    except Exception as e:
        logger.exception("An error occurred in aouth_callback_login")
        messages.error(request, "An error occurred during login", extra_tags='aouth_callback_login')
        return redirect('login')

# LOUGOUT
# -------
    
def aouth_logout(request):
    if request.user.is_authenticated:
        user_set_is_connected(request.user, False)
        logout(request)
    return redirect('login')
    
    