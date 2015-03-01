from django.db import models
from django.contrib.auth import models as auth_models

# Create your models here.


class User(auth_models.User):
    def __str__(self):
        return self.first_name + " " + self.last_name
