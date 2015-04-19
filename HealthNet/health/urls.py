from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
from . import views

# Make sure to end each URL pattern with '/?$' to make sure the end of the url
# properly handles omitting the trailing slash.
urlpatterns = patterns('',
    url(r'login/?$', views.login_view, name='login'),
    url(r'logout/?$', views.logout_view, name='logout'),
    url(r'schedule/?$', views.schedule, name='schedule'),
    url(r'prescriptions/?$', views.prescriptions, name='prescriptions'),
    url(r'delete_prescription/(\d+)/?$', views.delete_prescription, name='delete_prescription'),
    url(r'users/(\d+)/?$', views.profile, name='profile'),
    url(r'signup/?$', views.signup, name='signup'),
    url(r'logs/?$', views.logs, name='logs'),
    url(r'^/?$', views.my_profile, name='my_profile'),
)