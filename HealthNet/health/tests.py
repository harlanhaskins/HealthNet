from django.test import TestCase
import datetime
from .models import *


class UserTestCase(TestCase):

    def setUp(self):
        """
        Creates many users in the database.
        """
        h = Hospital.objects.create(name="University of Rochester Medical Center",
                                    address="601 Elmwood Ave", state="New York", city="Rochester",
                                    zipcode="14620")

        h2 = Hospital.objects.create(name="RIT Health Center",
                                    address="1 Lomb Memorial Drive", state="New York", city="Rochester",
                                    zipcode="14623")

        h3 = Hospital.objects.create(name="Highland Hospital",
                                     address="1000 South Ave", state="New York", city="Rochester",
                                     zipcode="14620")

        patients = Group.objects.create(name="Patient")
        doctors = Group.objects.create(name="Doctor")
        nurses = Group.objects.create(name="Nurse")

        email = "admin@djangomaintained.com"
        admin = User.objects.create_superuser('admin', email=email, first_name="Administrator",
                last_name="Jones", password="SuperSecurePassword1234", phone_number="8649189255",
                hospital=h, date_of_birth=datetime.date(year=1995, month=4, day=27))

        email = "jd@sacredheart.org"
        doctor = User.objects.create_user(email, email=email, first_name="John",
                 last_name="Dorian", password="SuperSecurePassword1234", phone_number="18005553333",
                 hospital=h, date_of_birth=datetime.date(year=1980, month=6, day=7))
        doctors.user_set.add(doctor)
        email = "turk@sacredheart.org"
        doctor = User.objects.create_user(email, email=email, first_name="Christopher",
                 last_name="Turkleton", password="SuperSecurePassword1234", phone_number="18005553333",
                 hospital=h, date_of_birth=datetime.date(year=1980, month=6, day=7))
        doctors.user_set.add(doctor)
        email = "drcox@sacredheart.org"
        doctor = User.objects.create_user(email, email=email, first_name="Perry",
                 last_name="Cox", password="SuperSecurePassword1234", phone_number="18005553333",
                 hospital=h, date_of_birth=datetime.date(year=1980, month=6, day=7))
        doctors.user_set.add(doctor)

        email = "carla@sacredheart.org"
        nurse = User.objects.create_user(email, email=email, first_name="Carla",
                last_name="Turkleton", password="SuperSecurePassword1234", phone_number="18005553333",
                hospital=h, date_of_birth=datetime.date(year=1976, month=3, day=9))
        nurses.user_set.add(nurse)

        insurance = Insurance.objects.create(company="Hobo Sal's Used Needle Emporium",
                                             policy_number="8675309")

        medical_info = MedicalInformation.objects.create(sex='Male', insurance=insurance, medications=None,
                                                         allergies=None, medical_conditions="Brain Tumor",
                                                         family_history=None, additional_info="Oh, you guys!")
        email = "duwayne@theroc-johnson.com"
        patient = User.objects.create_user(email, email=email, first_name="Duwayne",
                  last_name="Theroc-Johnson", password="SuperSecurePassword1234", phone_number="18005553333",
                  hospital=h, date_of_birth=datetime.date(year=1991, month=3, day=29), medical_information=medical_info)

        patients.user_set.add(patient)

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