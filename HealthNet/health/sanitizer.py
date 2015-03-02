__author__ = 'harlanhaskins'
import re


def sanitize_phone(number):
    if not number:
        return None
    regex = re.compile(r'[^\d.]+')
    return regex.sub('', number)