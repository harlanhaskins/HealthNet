__author__ = 'harlanhaskins'
from .models import Log
from datetime import datetime

def logged(action):
    def decorator(a_view):
        def _wrapped_view(request, *args, **kwargs):
            Log.objects.create(user=request.user, action=action,
                               date=datetime.now())
            return a_view(request, *args, **kwargs)
        return _wrapped_view
    return decorator