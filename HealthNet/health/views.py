from django.shortcuts import render, redirect
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from . import sanitizer
from . import checks
from .models import *
from .decorators import *
import datetime


@login_required
def index(request):
    return render(request, 'index.html', {"user": request.user,
                                          "navbar":"home"})


def login_view(request):
    if request.POST:
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(username=email, password=password)
        remember = request.POST.get("remember")
        if user is not None:
            login(request, user)
            if remember is not None:
                request.session.set_expiry(0)
            return redirect('health:index')
    return render(request, 'registration/login.html', {'navbar':'login'})


def logout_view(request):
    logout(request)
    return redirect('health:index')

@login_required
@logged('viewed prescriptions')
def prescriptions(request):
    context = {
        "navbar":"prescriptions",
        "user": request.user
    }
    return render(request, 'prescriptions.html', context)

static_signup_context = {
    "year_range": range(1900, datetime.date.today().year + 1),
    "day_range": range(1, 32),
    "months": [
        "Jan", "Feb", "Mar", "Apr",
        "May", "Jun", "Jul", "Aug",
        "Sep", "Oct", "Nov", "Dec"
    ]
}


def signup(request):
    if request.POST:
        password = request.POST.get("password")
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")

        email = request.POST.get("email")
        phone = sanitizer.sanitize_phone(request.POST.get("phone"))
        month = int(request.POST.get("month"))
        day = int(request.POST.get("day"))
        year = int(request.POST.get("year"))
        date = datetime.date(month=month, day=day, year=year)
        hospital_key = int(request.POST.get("hospital"))
        hospital = Hospital.objects.get(pk=hospital_key)
        if not User.objects.get(email=email):
            user = User.objects.create_user(email, email=email,
                password=password, date_of_birth=date, phone_number=phone,
                first_name=firstname, last_name=lastname, hospital=hospital)
            if user is not None:
                policy = request.POST.get("policy")
                company = request.POST.get("company")
                insurance = Insurance.objects.create(policy_number=policy,
                    company=company, patient=user)
                if insurance is not None:
                    return redirect('health:index')
    signup_context = dict(static_signup_context)
    signup_context['hospitals'] = Hospital.objects.all()
    return render(request, 'signup.html', signup_context)


@login_required
@logged('viewed schedule')
def schedule(request):
    context = {
        "navbar":"schedule",
        "user": request.user
    }
    return render(request, 'schedule.html', context)

@login_required
@user_passes_test(checks.admin_check)
@logged("viewed logs")
def logs(request):
    context = {
        "navbar": "logs",
        "user": request.user,
        "logs": Log.objects.all().order_by('-date')
    }
    return render(request, 'logs.html', context)

