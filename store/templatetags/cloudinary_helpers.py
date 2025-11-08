from django import template
from django.conf import settings
from django.templatetags.static import static

register = template.Library()


@register.filter
def cloud_url(image_field):
    """Return a full URL for an ImageField.

    - If Cloudinary is enabled, use cloudinary.utils to build a secure URL.
    - If the value is falsy, return a static placeholder path.
    - Otherwise, fall back to the field's .url attribute.
    """
    if not image_field:
        return static('images/placeholder.jpg')

    # image_field may be an ImageFieldFile or a string name
    name = getattr(image_field, 'name', image_field)
    if not name:
        return static('images/placeholder.jpg')

    if getattr(settings, 'USE_CLOUDINARY', False):
        try:
            from cloudinary.utils import cloudinary_url
            url, options = cloudinary_url(name, secure=True)
            return url
        except Exception:
            # Fall back to default behaviour if cloudinary isn't available
            try:
                return image_field.url
            except Exception:
                return static('images/placeholder.jpg')

    # Default: return the ImageField's URL
    try:
        return image_field.url
    except Exception:
        return static('images/placeholder.jpg')
