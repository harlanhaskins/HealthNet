from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=30)
    REQUIRED_FIELDS = ['date_of_birth', 'phone_number']

    def __str__(self):
        return self.first_name + " " + self.last_name


class Insurance(models.Model):
    policy_number = models.CharField(max_length=200)
    company = models.CharField(max_length=200)


class Appointment(models.Model):
    patient = models.ForeignKey(User, related_name="User")
    doctor = models.ForeignKey(User, related_name="Doctor")


class Unit(models.Model):
    name = models.CharField(max_length=200)
    abbreviation = models.CharField(max_length=200)


class Prescription(models.Model):
    name = models.CharField(max_length=200)
    dosage = models.FloatField()
    unit = models.ForeignKey(Unit)