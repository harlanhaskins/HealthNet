from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = patterns('',
    (r'login/?$', auth_views.login),
    (r'schedule/?$', views.schedule),
    (r'/?$', views.index),
)
