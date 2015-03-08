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

        Group.objects.create(name="Patient")
        Group.objects.create(name="Doctor")
        Group.objects.create(name="Nurse")

        email = "harlan@harlanhaskins.com"
        admin = User.objects.create_superuser('admin', email=email, first_name="Barack",
                last_name="Obama", password="poopsatan666", phone_number="8649189255",
                hospital=h, date_of_birth=datetime.date(year=1995, month=4, day=27))

    def handle(self, *args, **options):
        self._create_users()
