from django.db import models
from django.db.models import ForeignKey

from django.utils.translation import gettext_lazy as _

class CustomTestVariation(models.Model):
    class Zygosity(models.TextChoices):
        HOMOZYGOUS_REFERENCE = "HOMOZYGOUS_REFERENCE", _('Homozygous Reference')
        HETEROZYGOUS = "HETEROZYGOUS", _('Heterozygous')
        HOMOZYGOUS_ALTERNATE = "HOMOZYGOUS_ALTERNATE", _('Homozygous Alternate')

    class Classification(models.TextChoices):
        BENIGN = "BENIGN", _('Benign')
        LIKELY_BENIGN = "LIKELY_BENIGN", _('Likely Benign')
        VARIANT_UNCERTAIN_SIGNIFICANCE = "VARIANT_UNCERTAIN_SIGNIFICANCE", _('Variant of Uncertain Significance')
        LIKELY_PATHOGENIC = "LIKELY_PATHOGENIC", _('Likely Pathogenic')
        PATHOGENIC = "PATHOGENIC", _('Pathogenic')
        UNKNOWN = "UNKNOWN", _('Unknown')

    class Meta:
        db_table = 'custom_test_variation'

    variation = models.CharField(max_length=255)

    classification = models.CharField(max_length=255, choices=Classification.choices, default=Classification.UNKNOWN.value, blank=True)
    zygosity = models.CharField(max_length=255, choices=Zygosity.choices, default=Zygosity.HOMOZYGOUS_REFERENCE.value, blank=True)

    custom_test_gene = ForeignKey('CustomTestGene', on_delete=models.CASCADE)
