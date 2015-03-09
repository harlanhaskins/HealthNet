__author__ = 'harlanhaskins'
import re
from django.core import validators
from django.core.exceptions import ValidationError


def sanitize_phone(number):
    """
    Removes all non-digit characters from a string.
    Useful for storing phone numbers.
    """
    if not number:
        return None
    regex = re.compile(r'[^\d.]+')
    return regex.sub('', number)


def email_is_valid(email):
    """
    Wrapper for Django's email validator that returns a boolean
    instead of requiring a try/catch block.
    :param email: The email to validate
    :return: Whether or not the email conforms to RFC 2822.
    """
    try:
        validators.validate_email(email)
        return True
    except ValidationError:
        return False