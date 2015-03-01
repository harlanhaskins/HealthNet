from django.db import models
from datetime import timedelta
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=30)

    REQUIRED_FIELDS = ['date_of_birth', 'phone_number', 'email']

    def __repr__(self):
        return self.get_full_name()


class Insurance(models.Model):
    policy_number = models.CharField(max_length=200)
    company = models.CharField(max_length=200)


class Patient(User):
    insurance = models.ForeignKey(Insurance, null=True)
    def schedule(self):
        return Appointment.objects.filter(patient=self)

    class Meta:
        verbose_name = "Patient"
        verbose_name_plural = "Patients"


class Doctor(User):
    def schedule(self):
        return Appointment.objects.filter(doctor=self)

    def patients(self):
        # returns a unique list of all Patient objects that have appointments
        # with this doctor.
        return list(set(map(lambda a: a.patient, self.schedule())))

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

    class Meta:
        verbose_name = "Doctor"
        verbose_name_plural = "Doctors"


class Appointment(models.Model):
    patient = models.ForeignKey(Patient)
    doctor = models.ForeignKey(Doctor)
    date = models.DateTimeField()
    duration = models.IntegerField()


class Unit(models.Model):
    name = models.CharField(max_length=200)
    abbreviation = models.CharField(max_length=200)

    def __repr__(self):
        # "grams (g)"
        return "%s (%s)" % self.name, self.abbreviation


class Prescription(models.Model):
    patient = models.ForeignKey(Patient)
    name = models.CharField(max_length=200)
    dosage = models.FloatField()
    unit = models.ForeignKey(Unit)

    def __repr__(self):
        # "20mg of Ibuprofen for Jane Doe"
        return ("%s %f%s for %s" %
            self.name, self.dosage, self.unit.abbreviation, self.patient)


class Log(models.Model):
    description = models.CharField(max_length=200)
    date = models.DateTimeField()