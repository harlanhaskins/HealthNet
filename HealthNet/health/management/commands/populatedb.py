from django.core.management.base import BaseCommand
from health.models import *
import datetime


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def _create_users(self):
        h = Hospital.objects.create(name="University of Rochester Medical Center",
                                    address="601 Elmwood Ave", state="New York", city="Rochester",
                                    zipcode="14620")
        email = "harlan@harlanhaskins.com"
        admin = User.objects.create_superuser('admin', email=email, first_name="Barack",
                last_name="Obama", password="poopsatan666", phone_number="8649189255",
                hospital=h, date_of_birth=datetime.date(year=1995, month=4, day=27))

    def handle(self, *args, **options):
        self._create_users()
