from django.conf import settings
from django.template.defaultfilters import register


@register.simple_tag
def frontend_reset_password_url():
    return settings.FRONTEND_ADMIN_RESET_PASSWORD_URL
