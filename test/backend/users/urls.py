from django.shortcuts import render
from django.http import HttpResponse
from django.urls import path
from django.views.generic import TemplateView
from api.views import *
from users.views import *
from django.contrib import admin
from django.http import HttpResponseNotAllowed
from . import views

urlpatterns = [
	#path('accueil/', views.oauth_callback, name='accueil'),
    path('accueil2/', TemplateView.as_view(template_name='accueil.html'), name='accueil'),
	path('oauth_form/', oauth_form, name='oauth_form'),
]
