from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
    (r'login/?$', views.login),
    (r'/?$', views.index),
)
