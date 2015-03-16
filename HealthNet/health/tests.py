from django.test import TestCase
import datetime
from .models import *


class UserTestCase(TestCase):

    def setUp(self):
        self.hospital = Hospital.objects.create(name="University of Rochester Medical Center",
                                                address="601 Elmwood Ave", state="New York", city="Rochester",
                                                zipcode="14620")

        self.hospital2 = Hospital.objects.create(name="RIT Health Center",
                                                 address="1 Lomb Memorial Drive", state="New York", city="Rochester",
                                                 zipcode="14623")

        self.hospital3 = Hospital.objects.create(name="Highland Hospital",
                                                 address="1000 South Ave", state="New York", city="Rochester",
                                                 zipcode="14620")

        self.patients = Group.objects.create(name="Patient")
        self.doctors = Group.objects.create(name="Doctor")
        self.nurses = Group.objects.create(name="Nurse")

        email = "admin@djangomaintained.com"
        self.admin = User.objects.create_superuser('admin', email=email, first_name="Administrator",
                                                   last_name="Jones", password="SuperSecurePassword1234", phone_number="8649189255",
                                                   hospital=self.hospital, date_of_birth=datetime.date(year=1995, month=4, day=27))

        email = "jd@sacredheart.org"
        self.doctor = User.objects.create_user(email, email=email, first_name="John",
                                               last_name="Dorian", password="SuperSecurePassword1234", phone_number="18005553333",
                                               hospital=self.hospital, date_of_birth=datetime.date(year=1980, month=6, day=7))
        self.doctors.user_set.add(self.doctor)
        email = "turk@sacredheart.org"
        self.doctor2 = User.objects.create_user(email, email=email, first_name="Christopher",
                                                last_name="Turkleton", password="SuperSecurePassword1234", phone_number="18005553333",
                                                hospital=self.hospital, date_of_birth=datetime.date(year=1980, month=6, day=7))
        self.doctors.user_set.add(self.doctor2)
        email = "drcox@sacredheart.org"
        self.doctor3 = User.objects.create_user(email, email=email, first_name="Perry",
                                                last_name="Cox", password="SuperSecurePassword1234", phone_number="18005553333",
                                                hospital=self.hospital, date_of_birth=datetime.date(year=1980, month=6, day=7))
        self.doctors.user_set.add(self.doctor3)

        email = "carla@sacredheart.org"
        self.nurse = User.objects.create_user(email, email=email, first_name="Carla",
                                              last_name="Turkleton", password="SuperSecurePassword1234", phone_number="18005553333",
                                              hospital=self.hospital, date_of_birth=datetime.date(year=1976, month=3, day=9))
        self.nurses.user_set.add(self.nurse)

        self.insurance = Insurance.objects.create(company="Hobo Sal's Used Needle Emporium",
                                                  policy_number="8675309")
        email = "duwayne@theroc-johnson.com"
        self.patient = User.objects.create_user(email, email=email, first_name="Duwayne",
                                                last_name="Theroc-Johnson", password="SuperSecurePassword1234", phone_number="18005553333",
                                                hospital=self.hospital, date_of_birth=datetime.date(year=1991, month=3, day=29), insurance=self.insurance)

        self.patients.user_set.add(self.patient)

        self.unit = Unit.objects.create(name="milligrams", abbreviation="mg")
        self.unit2 = Unit.objects.create(name="grams", abbreviation="g")
        self.unit3 = Unit.objects.create(name="liters", abbreviation="L")
        self.unit4 = Unit.objects.create(name="milliliters", abbreviation="mL")

    def test_group_definitions(self):
        self.assertTrue(self.patient.is_patient())
        self.assertFalse(self.patient.is_doctor())
        self.assertFalse(self.patient.is_nurse())

        self.assertTrue(self.doctor.is_doctor())
        self.assertFalse(self.doctor.is_patient())
        self.assertFalse(self.doctor.is_nurse())

        self.assertTrue(self.nurse.is_nurse())
        self.assertFalse(self.nurse.is_patient())
        self.assertFalse(self.nurse.is_doctor())

    def test_can_add_prescription(self):
        self.assertTrue(self.doctor.can_add_prescription())
        self.assertFalse(self.patient.can_add_prescription())
        self.assertFalse(self.nurse.can_add_prescription())