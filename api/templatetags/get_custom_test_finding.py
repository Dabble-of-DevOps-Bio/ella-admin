from django.template.defaultfilters import register
from api.models import CustomTest


@register.filter
def get_custom_test_finding(value: str):
    return CustomTest.Finding(value).label
