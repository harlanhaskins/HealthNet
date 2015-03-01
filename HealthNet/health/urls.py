from django.conf.urls import patterns, include, url
from health import views

urlpatterns = patterns('',
    (r'login/$', 'django.contrib.auth.views.login')
)
