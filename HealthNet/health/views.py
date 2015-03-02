from django.shortcuts import render, redirect
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
import datetime

@login_required
def index(request):
    return render(request, 'index.html', {"user": request.user})


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

signup_context = {
    "year_range": range(1900, datetime.date.today().year + 1),
    "day_range": range(1, 32),
    "months": [
        "Jan", "Feb", "Mar", "Apr",
        "May", "Jun", "Jul", "Aug",
        "Sep", "Oct", "Nov", "Dec"
    ]
}


def signup(request):
    return render(request, 'signup.html', signup_context)


@login_required
def schedule(request):
    return render(request, 'schedule.html')