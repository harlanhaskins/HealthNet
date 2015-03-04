from django.db import models
from datetime import datetime, timedelta
from django.contrib.auth.models import AbstractUser


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

    REQUIRED_FIELDS = ['date_of_birth', 'phone_number', 'email', 'first_name',
                       'last_name', 'hospital']

    def all_patients(self):
        if self.is_superuser:
            # Admins can see all users as patients.
            return User.objects.all()
        elif self.groups.filter(name="Doctor"):
            # Doctors get all users who have active appointments.
            # Map Appointment.patient over the list of appointments
            # to get all patients associated with appointments, then
            # put them into a set and back into a list to get rid of duplicates.
            return list(set(map(Appointment.patient,
                        Appointment.objects.filter(doctor=self).values())))
        else:
            # Users can only see themselves.
            return [self]

    def active_patients(self):
        return self.all_patients().filter(is_active=True)

    def schedule(self):
        if self.groups.filter(name="Doctor"):
            # Doctors see all appointments for which they are needed.
            return Appointment.objects.filter(doctor=self)
        elif self.groups.filter(name="Nurse") or self.is_superuser:
            # Nurses and admins see all appointments.
            return Appointment.objects.all()
        # Patients see all appointments
        return Appointment.objects.filter(patient=self)

    def is_free(self, date, duration):
        schedule = self.schedule()
        end = date + duration
        for appointment in schedule:
            # If the dates intersect (meaning one starts while the other is
            # in progress) then the person is not free at the provided date
            # and time.
            if (date <= appointment.date <= end or
                    appointment.date <= date <= appointment.end()):
                return False
        return True


class Insurance(models.Model):
    policy_number = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    patient = models.ForeignKey(User)


class Appointment(models.Model):
    patient = models.ForeignKey(User, related_name='Patient')
    doctor = models.ForeignKey(User, related_name='Doctor')
    date = models.DateTimeField()
    duration = models.IntegerField()

    def end(self):
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