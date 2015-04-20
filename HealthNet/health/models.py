from django.db import models
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractUser, Group


class Insurance(models.Model):
    policy_number = models.CharField(max_length=200)
    company = models.CharField(max_length=200)


class EmergencyContact(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=30)
    relationship = models.CharField(max_length=30)


class MedicalInformation(models.Model):
    SEX_CHOICES = (
        'Female',
        'Male',
        'Intersex',
    )
    sex = models.CharField(max_length=50)
    insurance = models.ForeignKey(Insurance)
    medications = models.CharField(max_length=200, null=True)
    allergies = models.CharField(max_length=200, null=True)
    medical_conditions = models.CharField(max_length=200, null=True)
    family_history = models.CharField(max_length=200, null=True)
    additional_info = models.CharField(max_length=400, null=True)


class Hospital(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=2)
    zipcode = models.CharField(max_length=20)

    def __repr__(self):
        # "St. Jude Hospital at 1 Hospital Road, Waterbury, CT 06470"
        return ("%s at %s, %s, %s %s" % self.name, self.address, self.city,
                self.state, self.zipcode)


class User(AbstractUser):
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=30)
    hospital = models.ForeignKey(Hospital, null=True)
    medical_information = models.ForeignKey(MedicalInformation, null=True)
    emergency_contact = models.ForeignKey(EmergencyContact, null=True)

    REQUIRED_FIELDS = ['date_of_birth', 'phone_number', 'email', 'first_name',
                       'last_name', 'hospital']

    def all_patients(self):
        """
        Returns all patients relevant for a given user.
        If the user is a doctor:
            Returns all patients with active appointments with the doctor.
        If the user is a patient:
            Returns themself.
        If the user is an admin:
            Returns all patients in the database.
        :return:
        """
        if self.is_superuser or self.is_doctor():
            # Admins and doctors can see all users as patients.
            return Group.objects.get(name='Patient').user_set.all()
        elif self.is_nurse():
            # Nurses get all users inside their hospital.
            return User.objects.filter(hospital=self.hospital)
        else:
            # Users can only see themselves.
            return User.objects.filter(pk=self.pk)

    def active_patients(self):
        """
        Same as all_patients, but only patients that are active.
        :return: All active patients relevant to the current user.
        """
        return self.all_patients().filter(is_active=True)

    def can_add_prescription(self):
        return self.is_superuser or self.is_doctor()

    def latest_messages(self):
        return Message.objects.filter(
            Q(sender=self) | Q(recipient=self)
        ).order_by('-date')

    def schedule(self):
        """
        :return: All appointments for which this person is needed.
        """
        if self.is_superuser:
            return Appointment.objects.all()
        elif self.is_doctor():
            # Doctors see all appointments for which they are needed.
            return Appointment.objects.filter(doctor=self)
        # Patients see all appointments
        return Appointment.objects.filter(patient=self)

    def is_patient(self):
        """
        :return: True if the user belongs to the Patient group.
        """
        return self.is_in_group("Patient")

    def is_nurse(self):
        """
        :return: True if the user belongs to the Nurse group.
        """
        return self.is_in_group("Nurse")

    def is_doctor(self):
        """
        :return: True if the user belongs to the Doctor group.
        """
        return self.is_in_group("Doctor")

    def is_in_group(self, group_name):
        """
        :param group_name: The group within which to check membership.
        :return: True if the user is a member of the group provided.
        """
        try:
            return (Group.objects.get(name=group_name)
                         .user_set.filter(pk=self.pk).exists())
        except ValueError:
            return False

    def group(self):
        return self.groups.first()

    def is_free(self, date, duration):
        """
        Checks the user's schedule for a given date and duration to see if
        the user does not have an appointment at that time.
        :param date:
        :param duration:
        :return:
        """
        schedule = self.schedule()
        date = timezone.make_aware(date,
                                  timezone.get_current_timezone())
        end = timezone.make_aware(date + timedelta(minutes=duration),
                                  timezone.get_current_timezone())
        for appointment in schedule:
            # If the dates intersect (meaning one starts while the other is
            # in progress) then the person is not free at the provided date
            # and time.
            if (date <= appointment.date <= end or
                    appointment.date <= date <= appointment.end()):
                return False
        return True


class Appointment(models.Model):
    patient = models.ForeignKey(User, related_name='patient_appointments')
    doctor = models.ForeignKey(User, related_name='doctor_appointments')
    date = models.DateTimeField()
    duration = models.IntegerField()

    def end(self):
        """
        :return: A datetime representing the end of the appointment.
        """
        return self.date + timedelta(seconds=self.duration)


class Prescription(models.Model):
    patient = models.ForeignKey(User)
    name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=200)
    directions = models.CharField(max_length=1000)


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages')
    recipient = models.ForeignKey(User, related_name='received_messages')
    subject = models.CharField(max_length=50)
    body = models.CharField(max_length=500)
    date = models.DateTimeField()
