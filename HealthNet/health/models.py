from django.db import models
from django.contrib.auth import models as auth_models


class User(auth_models.User):
    first_name = models.CharField()
    last_name = models.CharField()
    date_of_birth = models.DateField()
    schedule = models.ManyToManyField(Appointment)

    def __str__(self):
        return self.first_name + " " + self.last_name


class Insurance(models.Model):
    policy_number = models.CharField()
    company = models.CharField()


class Appointment(models.Model):
    patient = models.ForeignKey(User)
    doctor = models.ForeignKey(User)


class Prescription(models.Model):
    name = models.CharField()
    dosage = models.FloatField()
    unit = models.ForeignKey(Unit)


class Unit(models.Model):
    name = models.CharField()
    abbreviation = models.CharField()