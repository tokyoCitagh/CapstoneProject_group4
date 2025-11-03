from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """
    Splits the string using the provided argument as the delimiter.
    """
    if not isinstance(value, str):
        return value
        
    return value.split(arg)