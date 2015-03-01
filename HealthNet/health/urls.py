from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
    (r'login/?$', views.login),
    (r'schedule/?$', views.schedule),
    (r'/?$', views.index),
)
