from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = patterns('',
    url(r'login/?$', views.login_view, name='login'),
    url(r'logout/?$', views.logout_view, name='logout'),
    url(r'schedule/?$', views.schedule, name='schedule'),
    url(r'prescriptions/?$', views.prescriptions, name='prescriptions'),
    url(r'signup/?$', views.signup, name='signup'),
    url(r'/?$', views.index, name='index'),
)

