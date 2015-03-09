__author__ = 'harlanhaskins'
from .models import Log
from django.utils import timezone


def logged(action):
    """
    Wraps a Django view and creates a Log based on the supplied action.
    If the request is a GET request, it prepends 'viewed ', and if the request
    is a POST request, prepends 'modified '
    :param action: The action being triggered, like "schedule" or "profile"
    :return: A triple-nested decorator that wraps a view and logs the provided
    action.
    """
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