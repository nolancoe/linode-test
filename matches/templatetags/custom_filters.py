# custom_filters.py
from django import template
from django.utils import timezone
from pytz import timezone as pytz_timezone

register = template.Library()

@register.filter
def convert_to_user_timezone(value, user):
    if user and user.timezone:
        user_tz = pytz_timezone(user.timezone)  # Convert the string to a valid timezone object
        return timezone.localtime(value, timezone=user_tz)
    return value
