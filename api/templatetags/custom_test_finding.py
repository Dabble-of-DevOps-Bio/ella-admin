from django.template.defaultfilters import register
from api.models import CustomTest


@register.filter
def custom_test_finding(finding: CustomTest.Finding):
    return finding.title()
