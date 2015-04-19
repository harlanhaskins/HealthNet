from django.shortcuts import render, redirect, get_object_or_404
from django.utils import dateparse
from django.core.exceptions import PermissionDenied
from django.contrib.auth import logout, login, authenticate
from django.contrib.admin.models import LogEntry
from django.contrib.auth.decorators import login_required, user_passes_test
from . import form_utilities
from . import checks
from .models import *
import datetime


def login_view(request):
    """
    Presents a simple form for logging in a user.
    If requested via POST, looks for the username and password,
    and attempts to log the user in. If the credentials are invalid,
    it passes an error message to the context which the template will
    render using a Bootstrap alert.

    :param request: The Django request object.
    :return: The rendered 'login' page.
    """
    context = {'navbar':'login'}
    if request.POST:
        user, message = login_user_from_form(request, request.POST)
        if user:
            return redirect('health:my_profile')
        elif message:
            context['error_message'] = message
    return render(request, 'login.html', context)


def login_user_from_form(request, body):
    """
    Validates a user's login credentials and returns a tuple
    containing either a valid, logged-in user or a failure
    message.

    Checks if all fields were supplied, then attempts to authenticate,
    then checks if the 'remember' checkbox was checked. If it was, sets
    the cookie's expiration to 0, meaning it will be invalidated when the
    session ends.

    :param request: The Django request object.
    :return: The rendered 'login' page.
    """
    email = body.get("email")
    password = body.get("password")
    if not all([email, password]):
        return None, "You must provide an email and password."
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
    """
    Logs the user out and redirects the user to the login page.
    :param request: The Django request.
    :return: A 301 redirect to the login page.
    """
    logout(request)
    return redirect('health:login')


def create_prescription_from_form(body):
    name = body.get("name")
    dosage = body.get("dosage")
    patient = body.get("patient")
    directions = body.get("directions")
    if not all([name, dosage, patient, directions]):
        return None, "All fields are required."
    try:
        patient = User.objects.get(pk=int(patient))
    except ValueError:
        return None, "We could not find the user specified."

    p = Prescription.objects.create(name=name, dosage=dosage,
                                    patient=patient, directions=directions)
    if not p:
        return None, "We could not create that prescription. Please try again."
    return p, None


def modify_prescription_from_form(body, prescription):
    name = body.get("name")
    dosage = body.get("dosage")
    patient = body.get("patient")
    directions = body.get("directions")
    if not all([name, dosage, patient, directions]):
        return None, "All fields are required."
    try:
        patient = User.objects.get(pk=int(patient))
    except ValueError:
        return None, "We could not find the user specified."

    prescription.name = name
    prescription.dosage = dosage
    prescription.patient = patient
    prescription.directions = directions

    prescription.save()

    return prescription, None

@login_required
def prescriptions(request):
    """
    Renders a table of the prescriptions associated with this user.

    :param request: The Django request.
    :return: A rendered version of prescriptions.html
    """
    context = {
        "navbar":"prescriptions",
        "logged_in_user": request.user,
    }

    return render(request, 'prescriptions.html', context)


def add_prescription_form(request):
    return prescription_form(request, None)


def prescription_form(request, prescription_id):
    prescription = None
    if prescription_id:
        prescription = get_object_or_404(Prescription, pk=prescription_id)
    if request.POST:
        if not request.user.can_add_prescription():
            raise PermissionDenied
        if prescription:
            p, message = modify_prescription_from_form(request.POST, prescription)
        else:
            p, message = create_prescription_from_form(request.POST)
        if p:
            return redirect('health:prescriptions')
    context = {
        'prescription': prescription,
        'logged_in_user': request.user
    }
    return render(request, 'edit_prescription.html', context)


def delete_prescription(request, prescription_id):
    p = get_object_or_404(Prescription, pk=prescription_id)
    p.delete()
    return redirect('health:prescriptions')


def signup(request):
    """
    Presents a simple signup page with a form of all the required
    fields for new users.
    Uses the full_signup_context function to populate a year/month/day picker
    and, if the user was created successfully, prompts the user to log in.
    :param request:
    :return:
    """
    context = full_signup_context()
    if request.POST:
        user, message = create_user_from_form(request.POST)
        if user:
            return redirect('health:login')
        elif message:
            context['error_message'] = message
    return render(request, 'signup.html', context)


def full_signup_context():
    """
    Returns a dictionary containing valid years, months, days, hospitals,
    and groups in the database.
    """
    return {
        "year_range": range(1900, datetime.date.today().year + 1),
        "day_range": range(1, 32),
        "months": [
            "Jan", "Feb", "Mar", "Apr",
            "May", "Jun", "Jul", "Aug",
            "Sep", "Oct", "Nov", "Dec"
        ],
        "hospitals": Hospital.objects.all(),
        "groups": Group.objects.all(),
        "sexes": MedicalInformation.SEX_CHOICES
    }


@login_required
def my_profile(request):
    """
    Gets the primary key of the current user and redirects to the profile view
    for the logged-in user.
    :param request:
    :return:
    """
    return redirect('health:profile', request.user.pk)


@login_required
def profile(request, user_id):
    """
    Checks if the logged-in user has permission to modify the requested user.
    If not, raises a PermissionDenied which Django catches by redirecting to
    a 403 page.

    If requested via GET:
        Renders a page containing all the user's fields pre-filled-in
        with their information.
    If requested via POST:
        modifies the values and redirects to the same page, with the new values.
    :param request: The Django request.
    :param user_id: The user id being requested. This is part of the URL:
    /users/<user_id>/
    :return:
    """
    requested_user = get_object_or_404(User, pk=user_id)
    is_editing_own_profile = requested_user == request.user
    if not is_editing_own_profile and not request.user.is_superuser:
        raise PermissionDenied

    if request.POST:
        handle_user_form(request.POST, user=requested_user)
        return redirect('health:profile', user_id)

    context = full_signup_context()
    context["user"] = requested_user
    context["logged_in_user"] = request.user
    context["navbar"] = "my_profile" if is_editing_own_profile else "profile"
    return render(request, 'profile.html', context)


def handle_user_form(body, user=None):
    """
    Creates a user and validates all of the fields, in turn.
    If there is a failure in any validation, the returned tuple contains
    None and a failure message.
    If validation succeeds and the user can be created, then the returned tuple
    contains the user and None for a failure message.
    :param body: The POST body from the request.
    :return: A tuple containing the User if successfully created,
             or a failure message if the operation failed.
    """
    password = body.get("password")
    first_name = body.get("first_name")
    last_name = body.get("last_name")

    email = body.get("email")
    group = int(body.get("group"))
    phone = form_utilities.sanitize_phone(body.get("phone_number"))
    month = int(body.get("month"))
    day = int(body.get("day"))
    year = int(body.get("year"))
    date = datetime.date(month=month, day=day, year=year)
    hospital_key = int(body.get("hospital"))
    hospital = Hospital.objects.get(pk=hospital_key)
    policy = body.get("policy")
    company = body.get("company")
    sex = body.get("sex")
    medications = body.get("medications")
    allergies = body.get("allergies")
    medical_conditions = body.get("medical_conditions")
    family_history = body.get("family_history")
    additional_info = body.get("additional_info")
    group = Group.objects.get(pk=group)
    if not all([password, first_name, last_name,
                email, phone, month, day, year, date]):
        return None, "All fields are required."
    email = email.lower()  # lowercase the email before adding it to the db.
    if not form_utilities.email_is_valid(email):
        return None, "Invalid email."
    if not all([company, policy]):
        return None, "Insurance information is required."
    if user:
        user.email = email
        user.phone_number = phone
        user.first_name = first_name
        user.last_name = last_name
        user.date_of_birth = date
        if not user.medical_information:
            insurance = Insurance.objects.create(policy_number=policy,
                                                 company=company)
            medical_information = MedicalInformation.objects.create(
                allergies=allergies, family_history=family_history,
                sex=sex, medications=medications,
                additional_info=additional_info, insurance=insurance,
                medical_conditions=medical_conditions
            )
            user.medical_information = medical_information
        if user.hospital != hospital:
            user.hospital.user_set.remove(user)
            user.hospital.save()
            user.hospital = hospital
        group_id = body.get("group")
        if group_id and user.is_superuser:
            group_id = int(group_id)
            if not user.groups.filter(pk=group_id).exists():
                for group in user.groups.all():
                    group.user_set.remove(user)
                    group.save()
                group = Group.objects.get(pk=group_id)
                group.user_set.add(user)
                group.save()
        user.save()
        return user, None
    else:
        if User.objects.filter(email=email).exists():
            return None, "A user with that email already exists."
        insurance = Insurance.objects.create(policy_number=policy,
            company=company)
        if not insurance:
            return None, "We could not create that user. Please try again."
        medical_information = MedicalInformation.objects.create(
            allergies=allergies, family_history=family_history,
            sex=sex, medications=medications,
            additional_info=additional_info, insurance=insurance,
            medical_conditions=medical_conditions
        )
        user = User.objects.create_user(email, email=email,
            password=password, date_of_birth=date, phone_number=phone,
            first_name=first_name, last_name=last_name, hospital=hospital,
            medical_information=medical_information)
        if user is None:
            return None, "We could not create that user. Please try again."
        group.user_set.add(user)
        return user, None

def messages(request):
    context = {
        'navbar': 'messages',
        'user': request.user
    }
    return render(request, 'messages.html', context)


def create_appointment_from_form(body, user):
    """
    Validates the provided fields for an appointment request and creates one
    if all fields are valid.
    :param body: The HTTP form body containing the fields.
    :param user: The user intending to create the appointment.
    :return: A tuple containing either a valid appointment or failure message.
    """
    date_string = body.get("date")
    try:
        parsed = dateparse.parse_datetime(date_string)
        parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
        if not parsed:
            return None, "Invalid date or time."
    except ValueError:
        return None, "Invalid date or time."
    duration = int(body.get("duration"))
    doctor_id = int(body.get("doctor", user.pk))
    doctor = User.objects.get(pk=doctor_id)
    if not doctor.is_free(parsed, duration):
        return None, "The doctor is not free at that time." +\
                     " Please specify a different time."

    patient_id = int(body.get("patient", user.pk))
    patient = User.objects.get(pk=patient_id)
    if not patient.is_free(parsed, duration):
        return None, "The patient is not free at that time." +\
                     " Please specify a different time."

    appointment = Appointment.objects.create(date=parsed, duration=duration,
                                             doctor=doctor, patient=patient)

    if not appointment:
        return None, "We could not create the appointment. Please try again."
    return appointment, None


@login_required
def schedule(request):
    """
    If requested with GET:
        Renders a page with an HTML form allowing the user to add an appointment
        with an existing doctor.
        Also shows a table of the existing appointments for the logged-in user.
    If requested with POST:
        Looks for the form fields rendered by the template and creates an
        Appointment object corresponding to the fields provided.
    :param request:
    """

    context = {
        "navbar": "schedule",
        "user": request.user,
        "doctors": Group.objects.get(name="Doctor").user_set.all().order_by('first_name', 'last_name'),
        "patients": Group.objects.get(name="Patient").user_set.all().order_by('first_name', 'last_name')
    }

    if request.POST:
        appointment, message = create_appointment_from_form(request.POST,
                                                            request.user)
        if appointment:
            return redirect('health:schedule')
        elif message:
            context['error_message'] = message
    return render(request, 'schedule.html', context)

@login_required
@user_passes_test(checks.admin_check)
def logs(request):
    context = {
        "navbar": "logs",
        "user": request.user,
        "logs": LogEntry.objects.all().order_by('-action_time')
    }
    return render(request, 'logs.html', context)

@login_required
def medical_information(request):
    context = {
        "navbar": "medical_information",
        "user": request.user,
    }
    return render(request, 'medical_information.html', context)

