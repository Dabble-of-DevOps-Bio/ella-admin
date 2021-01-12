from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomReportTest(models.Model):
    class Type(models.TextChoices):
        MLPA = "MLPA", _('MLPA')
        SEQ = "SEQ", _('SEQ')
        NGS = "NGS", _('NGS')

    class Meta:
        db_table = 'custom_report_test'

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=Type.choices, default=Type.MLPA.value)

    method = models.TextField(blank=True)
    disclaimer = models.TextField(blank=True)
