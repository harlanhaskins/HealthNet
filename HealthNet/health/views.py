from django.shortcuts import render, redirect, get_object_or_404
from django.utils import dateparse
from django.core.exceptions import PermissionDenied
from django.contrib.admin.models import LogEntry
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.db.models import Q
from . import form_utilities
from .form_utilities import *
from . import checks
from .models import *
import datetime
import json


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
            return redirect('health:my_medical_information')
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


def handle_prescription_form(request, body, prescription=None):
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

    if prescription:
        changed_fields = []
        if prescription.name != name:
            changed_fields.append('name')
            prescription.name = name
        if prescription.dosage != dosage:
            changed_fields.append('dosage')
            prescription.dosage = dosage
        if prescription.directions != directions:
            changed_fields.append('directions')
            prescription.directions = directions
        if prescription.patient != patient:
            changed_fields.append('patient')
            prescription.patient = patient
        prescription.save()
        change(request, prescription, changed_fields)
    else:
        prescription = Prescription.objects.create(name=name, dosage=dosage,
                                        patient=patient, directions=directions)

        if not prescription:
            return None, "We could not create that prescription. Please try again."
        addition(request, prescription)
    return prescription, None


@login_required
def prescriptions(request, error=None):
    """
    Renders a table of the prescriptions associated with this user.

    :param request: The Django request.
    :return: A rendered version of prescriptions.html
    """
    context = {
        "navbar":"prescriptions",
        "logged_in_user": request.user,
    }
    if error:
        context["error_message"] = error

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
        p, message = handle_prescription_form(request, request.POST, prescription)
        return prescriptions(request, error=message)
    context = {
        'prescription': prescription,
        'logged_in_user': request.user
    }
    return render(request, 'edit_prescription.html', context)


def delete_prescription(request, prescription_id):
    p = get_object_or_404(Prescription, pk=prescription_id)
    p.delete()
    deletion(request, p, repr(p))
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
    context = full_signup_context(None)
    context['is_signup'] = True
    if request.POST:
        user, message = handle_user_form(request, request.POST)
        if user:
            addition(request, user)
            if request.user.is_authenticated():
                return redirect('health:signup')
            else:
                return redirect('health:login')
        elif message:
            context['error_message'] = message
    return render(request, 'signup.html', context)


def full_signup_context(user):
    """
    Returns a dictionary containing valid years, months, days, hospitals,
    and groups in the database.
    """
    return {
        "year_range": reversed(range(1900, datetime.date.today().year + 1)),
        "day_range": range(1, 32),
        "months": [
            "Jan", "Feb", "Mar", "Apr",
            "May", "Jun", "Jul", "Aug",
            "Sep", "Oct", "Nov", "Dec"
        ],
        "hospitals": Hospital.objects.all(),
        "groups": Group.objects.all(),
        "sexes": MedicalInformation.SEX_CHOICES,
        "user_sex_other": (user and user.medical_information and
            user.medical_information.sex not in MedicalInformation.SEX_CHOICES)
    }

@login_required
def add_group(request):
    context = {}
    if request.POST:
        group, message = handle_add_group_form(request, request.POST)
        if group:
            addition(request, group)
        elif message:
            context['error_message'] = message
    return redirect('health:messages')


def handle_add_group_form(request, body):
    name = request.POST.get('name')
    recipient_id = request.POST.get('recipient')
    message = request.POST.get('message')

    if not all([name, recipient_id, message]):
        return None, "All fields are required."
    if not recipient_id.isdigit():
        return None, "Invalid recipient."
    group = MessageGroup.objects.create(
        name=name
    )
    try:
        recipient = User.objects.get(pk=int(recipient_id))
    except User.DoesNotExist:
        return None, "Could not find user."
    group.members.add(request.user)
    group.members.add(recipient)
    group.save()
    Message.objects.create(sender=request.user, body=message,
                           group=group, date=timezone.now())
    return group, None

@login_required
def my_medical_information(request):
    """
    Gets the primary key of the current user and redirects to the medical_information view
    for the logged-in user.
    :param request:
    :return:
    """
    return medical_information(request, request.user.pk)


@login_required
def medical_information(request, user_id):
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
    is_editing_own_medical_information = requested_user == request.user
    if not is_editing_own_medical_information and not\
            request.user.can_edit_user(requested_user):
        raise PermissionDenied

    if request.POST:
        handle_user_form(request, request.POST, user=requested_user)
        return redirect('health:medical_information', user_id)

    context = full_signup_context(requested_user)
    context["requested_user"] = requested_user
    context["user"] = request.user
    context['is_signup'] = False
    context["navbar"] = "my_medical_information" if is_editing_own_medical_information else "medical_information"
    return render(request, 'medical_information.html', context)


def handle_user_form(request, body, user=None):
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
    group = body.get("group")
    patient_group = Group.objects.get(name='Patient')
    group = Group.objects.get(pk=int(group)) if group else patient_group
    is_patient = group == patient_group
    phone = form_utilities.sanitize_phone(body.get("phone_number"))
    month = int(body.get("month"))
    day = int(body.get("day"))
    year = int(body.get("year"))
    date = datetime.date(month=month, day=day, year=year)
    hospital_key = body.get("hospital")
    hospital = Hospital.objects.get(pk=int(hospital_key)) if hospital_key else None
    policy = body.get("policy")
    company = body.get("company")
    sex = body.get("sex")
    other_sex = body.get("other_sex")
    medications = body.get("medications")
    allergies = body.get("allergies")
    medical_conditions = body.get("medical_conditions")
    family_history = body.get("family_history")
    additional_info = body.get("additional_info")
    if not all([first_name, last_name, email, phone,
                month, day, year, date]):
        return None, "All fields are required."
    email = email.lower()  # lowercase the email before adding it to the db.
    if not form_utilities.email_is_valid(email):
        return None, "Invalid email."
    if (user and user.is_patient()) and not all([company, policy]):
        return None, "Insurance information is required."
    if user:
        user.email = email
        user.phone_number = phone
        user.first_name = first_name
        user.last_name = last_name
        user.date_of_birth = date
        if is_patient and user.medical_information is not None:
            user.medical_information.sex = sex if sex in MedicalInformation.SEX_CHOICES else other_sex
            user.medical_information.medical_conditions = medical_conditions
            user.medical_information.family_history = family_history
            user.medical_information.additional_info = additional_info
            user.medical_information.allergies = allergies
            user.medical_information.medications = medications
            if user.medical_information.insurance:
                user.medical_information.insurance.policy_number = policy
                user.medical_information.insurance.company = company
                user.medical_information.insurance.save()
            else:
                user.medical_information.insurance = Insurance.objects.create(
                    policy_number=policy,
                    company=company
                )
                addition(request, user.medical_information.insurance)
            user.medical_information.save()
            change(request, user.medical_information, 'Changed fields.')
        elif user.is_patient():
            insurance = Insurance.objects.create(policy_number=policy,
                                                 company=company)
            addition(request, insurance)
            medical_information = MedicalInformation.objects.create(
                allergies=allergies, family_history=family_history,
                sex=sex, medications=medications,
                additional_info=additional_info, insurance=insurance,
                medical_conditions=medical_conditions
            )
            addition(request, user.medical_information)
            user.medical_information = medical_information
        if user.hospital != hospital:
            user.hospital = hospital
        if user.is_superuser:
            if not user.groups.filter(pk=group.pk).exists():
                for user_group in user.groups.all():
                    user_group.user_set.remove(user)
                    user_group.save()
                group.user_set.add(user)
                group.save()
        user.save()
        change(request, user, 'Changed fields.')
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
        request.user = user
        addition(request, user)
        addition(request, medical_information)
        addition(request, insurance)
        group.user_set.add(user)
        return user, None

@login_required
def messages(request):
    if request.user.is_patient():
        recipients = Group.objects.filter(Q(name='Doctor') | Q(name='Nurse'))
    else:
        recipients = request.user.all_patients()
    context = {
        'navbar': 'messages',
        'user': request.user,
        'recipients': recipients,
    }
    return render(request, 'messages.html', context)


def conversation(request, id):
    group = get_object_or_404(MessageGroup, pk=id)
    context = {
        "user": request.user,
        "group": group
    }
    if request.POST:
        message = request.POST.get('message')
        if message:
            msg = Message.objects.create(sender=request.user, group=group,
                                         body=message, date=timezone.now())
            group.messages.add(msg)
            group.save()
            # redirect to avoid the issues with reloading
            # sending the message again.
            return redirect('health:conversation', group.pk)
    return render(request, 'conversation.html', context)


def handle_appointment_form(request, body, user, appointment=None):
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
        if not parsed:
            return None, "Invalid date or time."
        parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
    except:
        return None, "Invalid date or time."
    duration = int(body.get("duration"))
    doctor_id = int(body.get("doctor", user.pk))
    doctor = User.objects.get(pk=doctor_id)
    patient_id = int(body.get("patient", user.pk))
    patient = User.objects.get(pk=patient_id)

    is_change = appointment is not None

    changed = []
    if is_change:
        if appointment.date != parsed:
            changed.append('date')
        if appointment.patient != patient:
            changed.append('patient')
        if appointment.duration != duration:
            changed.append('duration')
        if appointment.doctor != doctor:
            changed.append('doctor')
        appointment.delete()
    if not doctor.is_free(parsed, duration):
        return None, "The doctor is not free at that time." +\
                     " Please specify a different time."

    if not patient.is_free(parsed, duration):
        return None, "The patient is not free at that time." +\
                     " Please specify a different time."
    appointment = Appointment.objects.create(date=parsed, duration=duration,
                                             doctor=doctor, patient=patient)

    if is_change:
        change(request, appointment, changed)
    else:
        addition(request, appointment)
    if not appointment:
        return None, "We could not create the appointment. Please try again."
    return appointment, None


def appointment_form(request, appointment_id):
    appointment = None
    if appointment_id:
        appointment = get_object_or_404(Appointment, pk=appointment_id)
    if request.POST:
        appointment, message = handle_appointment_form(
            request, request.POST,
            request.user, appointment=appointment
        )
        return schedule(request, error=message)
    context = {
        "user": request.user,
        'appointment': appointment,
        "doctors": Group.objects.get(name="Doctor").user_set.all().order_by('first_name', 'last_name'),
        "patients": Group.objects.get(name="Patient").user_set.all().order_by('first_name', 'last_name')
    }
    return render(request, 'edit_appointment.html', context)

@login_required
def schedule(request, error=None):
    """
    Renders a page with an HTML form allowing the user to add an appointment
    with an existing doctor.
    Also shows a table of the existing appointments for the logged-in user.
    """
    now = timezone.now()

    context = {
        "navbar": "schedule",
        "user": request.user,
        "doctors": Group.objects.get(name="Doctor").user_set.all().order_by('first_name', 'last_name'),
        "patients": Group.objects.get(name="Patient").user_set.all().order_by('first_name', 'last_name'),
        "schedule_future": request.user.schedule().filter(date__gte=now).order_by('date'),
        "schedule_past": request.user.schedule().filter(date__lt=now).order_by('-date')
    }
    if error:
        context['error_message'] = error
    return render(request, 'schedule.html', context)


def add_appointment_form(request):
    return appointment_form(request, None)


def delete_appointment(request, appointment_id):
    a = get_object_or_404(Appointment, pk=appointment_id)
    a.delete()
    return redirect('health:schedule')


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
def home(request):
    return render(request, 'home.html', {'navbar': 'home',
                                         'user': request.user})

@login_required
def export(request):
    json_object = json.dumps(request.user.json_object(), sort_keys=True,
        indent=4, separators=(',', ': '))
    return HttpResponse(json_object,
        content_type='application/json', mimetype='application/force-download')