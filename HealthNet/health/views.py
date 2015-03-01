from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def index(request):
    return render(request, 'index.html', {"user":request.user})


@login_required
def schedule(request):
    return render(request, 'schedule.html', None)