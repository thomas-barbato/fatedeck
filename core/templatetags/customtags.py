from django import template
from datetime import datetime

register = template.Library()


@register.filter(name="today")
def today(date):
    return date >= datetime.today().date()


@register.filter(name='range')
def filter_range(start, end):
    return range(start, end)