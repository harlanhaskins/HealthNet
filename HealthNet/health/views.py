from django.shortcuts import render, redirect, get_object_or_404
from django.utils import dateparse
from django.core.exceptions import PermissionDenied
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from . import form_utilities
from . import checks
from .models import *
from .decorators import *
import datetime


def login_view(request):
    context = {'navbar':'login'}
    if request.POST:
        user, message = login_user_from_form(request, request.POST)
        if user:
            return redirect('health:my_profile')
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
    return redirect('health:login')

@login_required
@logged('prescriptions')
def prescriptions(request):
    context = {
        "navbar":"prescriptions",
        "user": request.user
    }
    return render(request, 'prescriptions.html', context)


def signup(request):
    context = full_signup_context()
    if request.POST:
        user, message = create_user_from_form(request.POST)
        if user:
            return redirect('health:login')
        elif message:
            context['error_message'] = message
    return render(request, 'signup.html', context)


def full_signup_context():
    return {
        "year_range": range(1900, datetime.date.today().year + 1),
        "day_range": range(1, 32),
        "months": [
            "Jan", "Feb", "Mar", "Apr",
            "May", "Jun", "Jul", "Aug",
            "Sep", "Oct", "Nov", "Dec"
        ],
        "hospitals": Hospital.objects.all(),
        "groups": Group.objects.all()
    }


def create_user_from_form(body):
    """
    :param body: The POST body from the request.
    :return: A tuple containing the User if successfully created,
             or a failure message if the operation failed.
    """
    password = body.get("password")
    firstname = body.get("first_name")
    lastname = body.get("last_name")

    email = body.get("email")
    group = body.get("group")
    phone = form_utilities.sanitize_phone(body.get("phone_number"))
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
    if not form_utilities.email_is_valid(email):
        return None, "Invalid email."
    if User.objects.filter(email=email).exists():
        return None, "A user with that email already exists."
    policy = body.get("policy")
    company = body.get("company")
    insurance = Insurance.objects.create(policy_number=policy,
        company=company)
    if not insurance:
        return None, "We could not create that user. Please try again."
    user = User.objects.create_user(email, email=email,
        password=password, date_of_birth=date, phone_number=phone,
        first_name=firstname, last_name=lastname, hospital=hospital,
        insurance=insurance)
    if user is None:
        return None, "We could not create that user. Please try again."
    group = Group.objects.get(pk=group)
    group.user_set.add(user)
    return user, None

@login_required
def my_profile(request):
    return redirect('health:profile', request.user.pk)

@login_required
@logged("profile")
def profile(request, user_id):
    requested_user = get_object_or_404(User, pk=user_id)
    is_editing_own_profile = requested_user == request.user
    if not is_editing_own_profile and not request.user.is_superuser:
        raise PermissionDenied

    if request.POST:
        modify_user_from_form(request.POST, request.user)
        return redirect('health:profile', user_id)

    context = full_signup_context()
    context["user"] = requested_user
    context["logged_in_user"] = request.user
    context["navbar"] = "my_profile" if is_editing_own_profile else "profile"
    return render(request, 'profile.html', context)


def modify_user_from_form(body, user):
    email = body.get("email")
    if email and user.email != email:
        user.email = email
    phone = form_utilities.sanitize_phone(body.get("phone_number"))
    if phone and user.phone_number != phone:
        user.phone_number = phone
    first_name = body.get("first_name")
    if first_name and user.first_name != first_name:
        user.first_name = first_name
    last_name = body.get("last_name")
    if last_name and user.last_name != last_name:
        user.last_name = last_name
    month = int(body.get("month"))
    day = int(body.get("day"))
    year = int(body.get("year"))
    date = datetime.date(month=month, day=day, year=year)
    if user.date_of_birth != date:
        user.date_of_birth = date
    company = body.get("company")
    policy = body.get("policy")
    if company and user.insurance.company != company:
        user.insurance.company = company
    if policy and user.insurance.policy_number != policy:
        user.insurance.policy_number = policy
    hospital_id = int(body.get("hospital"))
    current_hospital = user.hospital
    if user.hospital.pk != hospital_id:
        current_hospital.user_set.remove(user)
        current_hospital.save()
        user.hospital = Hospital.objects.get(pk=hospital_id)
    group_id = int(body.get("group"))
    if user.is_superuser:
        if not user.groups.filter(pk=group_id).exists():
            for group in user.groups.all():
                group.user_set.remove(user)
                group.save()
            group = Group.objects.get(pk=group_id)
            group.user_set.add(user)
            group.save()
    user.save()

@login_required
@logged('schedule')
def schedule(request):
    if request.POST:
        date_string = request.POST.get("date")
        parsed = dateparse.parse_datetime(date_string)
        duration = int(request.POST.get("duration"))
        doctor_id = int(request.POST.get("doctor"))
        doctor = Group.objects.get(name="Doctor").user_set.get(pk=doctor_id)
        appointment = Appointment.objects.create(date=parsed, duration=duration,
                                                 doctor=doctor, patient=request.user)
        if appointment:
            return redirect('health:schedule')
    context = {
        "navbar":"schedule",
        "user": request.user,
        "doctors": Group.objects.get(name="Doctor").user_set.all()
    }
    return render(request, 'schedule.html', context)


@login_required
@user_passes_test(checks.admin_check)
@logged("logs")
def logs(request):
    context = {
        "navbar": "logs",
        "user": request.user,
        "logs": Log.objects.all().order_by('-date')
    }
    return render(request, 'logs.html', context)

