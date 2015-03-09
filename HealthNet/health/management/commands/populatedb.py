from django.core.management.base import BaseCommand
from health.models import *
from django.contrib.auth.models import Group
import datetime


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def _create_users(self):
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

        email = "harlan@harlanhaskins.com"
        admin = User.objects.create_superuser('admin', email=email, first_name="Administrator",
                last_name="Jones", password="poopsatan666", phone_number="8649189255",
                hospital=h, date_of_birth=datetime.date(year=1995, month=4, day=27))

        email = "jd@sacredheart.org"
        doctor = User.objects.create_superuser(email, email=email, first_name="John",
                 last_name="Dorian", password="poopsatan666", phone_number="18005553333",
                 hospital=h, date_of_birth=datetime.date(year=1980, month=6, day=7))
        doctors.user_set.add(doctor)

        email = "carla@sacredheart.org"
        nurse = User.objects.create_superuser(email, email=email, first_name="Carla",
                last_name="Turkleton", password="poopsatan666", phone_number="18005553333",
                hospital=h, date_of_birth=datetime.date(year=1976, month=3, day=9))
        nurses.user_set.add(nurse)

        insurance = Insurance.objects.create(company="Hobo Sal's Used Needle Emporium",
                                             policy_number="8675309")
        email = "duwayne@theroc-johnson.com"
        patient = User.objects.create_superuser(email, email=email, first_name="Duwayne",
                  last_name="Theroc-Johnson", password="poopsatan666", phone_number="18005553333",
                  hospital=h, date_of_birth=datetime.date(year=1991, month=3, day=29), insurance=insurance)

        patients.user_set.add(patient)

    def handle(self, *args, **options):
        self._create_users()
