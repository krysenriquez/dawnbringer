from django import template
from django.utils.dateparse import parse_datetime
from datetime import datetime

register = template.Library()


@register.filter
def convert_str_date(value):
    return parse_datetime(value)
