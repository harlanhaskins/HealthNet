from django.shortcuts import render, RequestContext
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    return render(request, 'index.html', {"user": request.user})


def signup(request):
    return render(request, 'signup.html', None)

@login_required
def schedule(request):
    return render(request, 'schedule.html', None)