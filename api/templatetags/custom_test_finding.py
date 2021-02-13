from django.conf import settings
from django.template.defaultfilters import register


@register.simple_tag
def custom_test_finding():
    return settings.FRONTEND_ADMIN_RESET_PASSWORD_URL
