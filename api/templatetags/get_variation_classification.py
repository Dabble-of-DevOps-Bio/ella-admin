from django.template.defaultfilters import register
from api.models import CustomTestVariation


@register.filter
def get_variation_classification(value: str):
    return CustomTestVariation.Classification(value).label
