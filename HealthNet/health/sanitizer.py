__author__ = 'harlanhaskins'
import re
from django.core import validators
from django.core.exceptions import ValidationError


def sanitize_phone(number):
    if not number:
        return None
    regex = re.compile(r'[^\d.]+')
    return regex.sub('', number)


def email_is_valid(email):
    try:
        validators.validate_email(email)
        return True
    except ValidationError:
        return False