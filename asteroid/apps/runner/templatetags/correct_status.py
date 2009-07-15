"Template tag library"

from django import template

register = template.Library()

@register.filter('correct_status')
def correct_status(value):
    "Make friendlier formatting for status"
    # all we're actually doing is correcting the in_progress field
    if value == "in_progress":
        return "in progress"
    else:
        return value