from django.db import models
from datetime import timedelta
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=30)

    REQUIRED_FIELDS = ['date_of_birth', 'phone_number', 'email']

    def __repr__(self):
        return self.get_full_name()

    def schedule(self):
        if self.groups.filter(name="Doctor"):
            Appointment.objects.filter(doctor=self)
        elif self.groups.filter(name="Nurse"):
            return []
        return Appointment.objects.filter(patient=self)

    def is_free(self, date, duration):
        schedule = self.schedule()
        end = date + duration
        for appointment in schedule:
            appointment_end = (appointment.date +
                              timedelta(seconds=appointment.duration))
            if (date <= appointment.date <= end or
                    appointment.date <= date <= appointment_end):
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


class Unit(models.Model):
    name = models.CharField(max_length=200)
    abbreviation = models.CharField(max_length=200)


class Prescription(models.Model):
    patient = models.ForeignKey(User)
    name = models.CharField(max_length=200)
    dosage = models.FloatField()
    unit = models.ForeignKey(Unit)

    def full_dosage(self):
        return str(self.dosage) + self.unit.abbreviation


class Log(models.Model):
    description = models.CharField(max_length=200)
    date = models.DateTimeField()