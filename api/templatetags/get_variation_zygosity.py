from django.template.defaultfilters import register
from api.models import CustomTestVariation


@register.filter
def get_variation_zygosity(value: str):
    return CustomTestVariation.Zygosity(value).label
