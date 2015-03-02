from django.shortcuts import render, redirect
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    return render(request, 'index.html', {"user": request.user})


def signup(request):
    return render(request, 'signup.html')


def login_view(request):
    if request.POST:
        username = request.POST.get("username", None)
        password = request.POST.get("password", None)
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('health:index')
    return render(request, 'registration/login.html')


def logout_view(request):
    logout(request)
    return redirect('health:index')

@login_required
def prescriptions(request):
    return render(request, 'prescriptions.html')

@login_required
def schedule(request):
    return render(request, 'schedule.html')