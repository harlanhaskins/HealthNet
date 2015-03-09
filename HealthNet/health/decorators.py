__author__ = 'harlanhaskins'
from .models import Log
from django.utils import timezone


def logged(action):
    def decorator(a_view):
        def _wrapped_view(request, *args, **kwargs):
            new_action = action
            if request.method == "GET":
                new_action = "viewed " + action
            elif request.method == "POST":
                new_action = "modified " + action
            Log.objects.create(user=request.user, action=new_action,
                               date=timezone.now())
            return a_view(request, *args, **kwargs)
        return _wrapped_view
    return decorator