from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractUser, Group


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


class Insurance(models.Model):
    policy_number = models.CharField(max_length=200)
    company = models.CharField(max_length=200)


class User(AbstractUser):
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=30)
    hospital = models.ForeignKey(Hospital, null=True)
    insurance = models.ForeignKey(Insurance, null=True)

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
        if self.is_superuser:
            # Admins can see all users as patients.
            return Group.objects.get(name='Patient').user_set.all()
        elif self.groups.filter(name="Doctor").exists():
            # Doctors get all users who have active appointments.
            return (Appointment.objects.filter(doctor=self)
                                       .distinct('patient')
                                       .values('patient'))
        else:
            # Users can only see themselves.
            return User.objects.filter(pk=self.pk)

    def active_patients(self):
        """
        Same as all_patients, but only patients that are active.
        :return: All active patients relevant to the current user.
        """
        return self.all_patients().filter(is_active=True)

    def schedule(self):
        """
        :return: All appointments for which this person is needed.
        """
        if self.is_superuser:
            return Appointment.objects.all()
        elif self.groups.filter(name="Doctor").exists():
            # Doctors see all appointments for which they are needed.
            return Appointment.objects.filter(doctor=self)
        # Patients see all appointments
        return Appointment.objects.filter(patient=self)

    def is_patient(self):
        """
        :return: True if the user belongs to the Patient group.
        """
        return self.groups.filter(name="Patient").exists()

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
    patient = models.ForeignKey(User, related_name='Patient')
    doctor = models.ForeignKey(User, related_name='Doctor')
    date = models.DateTimeField()
    duration = models.IntegerField()

    def end(self):
        """
        :return: A datetime representing the end of the appointment.
        """
        return self.date + timedelta(seconds=self.duration)


class Unit(models.Model):
    name = models.CharField(max_length=200)
    abbreviation = models.CharField(max_length=200)


class Prescription(models.Model):
    patient = models.ForeignKey(User)
    name = models.CharField(max_length=200)
    dosage = models.FloatField()
    directions = models.CharField(max_length=1000)
    unit = models.ForeignKey(Unit)


class Log(models.Model):
    user = models.ForeignKey(User)
    action = models.CharField(max_length=200)
    date = models.DateTimeField()