from django.shortcuts import render, redirect
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from . import sanitizer
from . import checks
from .models import *
from .decorators import *
import datetime


@login_required
@logged('viewed home')
def index(request):
    return render(request, 'index.html', {"user": request.user,
                                          "navbar":"home"})


def login_view(request):
    context = {'navbar':'login'}
    if request.POST:
        user, message = login_user_from_form(request, request.POST)
        if user:
            return redirect('health:index')
        elif message:
            context['error_message'] = message
    return render(request, 'login.html', context)


def login_user_from_form(request, body):
    email = body.get("email")
    password = body.get("password")
    if not all([email, password]):
        return None, "You must provide a username and password."
    email = email.lower()  # all emails are lowercase in the database.
    user = authenticate(username=email, password=password)
    remember = body.get("remember")
    if user is None:
        return None, "Invalid username or password."
    login(request, user)
    if remember is not None:
        request.session.set_expiry(0)
    return user, None

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

# This should be evaluated once; these are the static values sent
# to the signup form to populate year, month, and day.
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
    signup_context = dict(static_signup_context)
    if request.POST:
        user, message = create_user_from_form(request.POST)
        if user:
            return redirect('health:login')
        elif message:
            signup_context['error_message'] = message
    signup_context['hospitals'] = Hospital.objects.all()
    return render(request, 'signup.html', signup_context)


# create_user_from_form(body: dict) -> (user: User?, message: String?)
def create_user_from_form(body):
    """
    :param body: The POST body from the request.
    :return: A tuple containing the User if successfully created,
             or a failure message if the operation failed.
    """
    password = body.get("password")
    firstname = body.get("firstname")
    lastname = body.get("lastname")

    email = body.get("email")
    phone = sanitizer.sanitize_phone(body.get("phone"))
    month = int(body.get("month"))
    day = int(body.get("day"))
    year = int(body.get("year"))
    date = datetime.date(month=month, day=day, year=year)
    hospital_key = int(body.get("hospital"))
    hospital = Hospital.objects.get(pk=hospital_key)
    if not all([password, firstname, lastname,
                email, phone, month, day, year, date]):
        return None, "All fields are required."
    email = email.lower()  # lowercase the email before adding it to the db.
    if not sanitizer.email_is_valid(email):
        return None, "Invalid email."
    if User.objects.filter(email=email).exists():
        return None, "A user with that email already exists."
    user = User.objects.create_user(email, email=email,
        password=password, date_of_birth=date, phone_number=phone,
        first_name=firstname, last_name=lastname, hospital=hospital)
    if user is None:
        return None, "We could not create that user. Please try again."
    policy = body.get("policy")
    company = body.get("company")
    insurance = Insurance.objects.create(policy_number=policy,
        company=company, patient=user)
    if not insurance:
        user.delete()
        return None, "We could not create that user. Please try again."
    return user, None

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

