from __future__ import absolute_import
from django import template

register = template.Library()

@register.filter
def get_range(i):
    return range(i)