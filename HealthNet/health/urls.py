from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = patterns('',
    url(r'login/?$', auth_views.login, name='login'),
    url(r'schedule/?$', views.schedule, name='schedule'),
    url(r'signup/?$', views.signup, name='signup'),
    url(r'/?$', views.index, name='index'),
)
