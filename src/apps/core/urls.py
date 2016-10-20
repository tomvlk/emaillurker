from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

from . import views


urlpatterns = [
	url(r'^search/$', views.SearchView.as_view(), name='search'),
]