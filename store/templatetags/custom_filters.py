# store/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def replace(value, arg):
    """
    Replaces all occurrences of a substring with another string.
    Usage: {{ value|replace:"old_text:new_text" }}
    
    The argument 'arg' is a string containing the old and new text 
    separated by a colon (e.g., "old_text:new_text").
    """
    if not isinstance(value, str):
        return value

    try:
        # Split the argument into the substring to replace (old) and the replacement (new)
        old, new = arg.split(':', 1)
        return value.replace(old, new)
    except ValueError:
        # If the argument format is incorrect, return the original value
        return value