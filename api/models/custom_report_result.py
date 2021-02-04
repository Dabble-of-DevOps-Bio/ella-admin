from django.db import models
from django.db.models import OneToOneField
from django.utils.translation import gettext_lazy as _


class CustomReportResult(models.Model):
    class Finding(models.TextChoices):
        POSITIVE = "POSITIVE", _('Positive')
        NEGATIVE = "NEGATIVE", _('Negative')
        INCONCLUSIVE = "INCONCLUSIVE", _('Inconclusive')

    class Meta:
        db_table = 'custom_report_result'

    result = models.TextField()
    finding = models.CharField(max_length=255, choices=Finding.choices, default=Finding.POSITIVE.value, blank=True)

    custom_report_test = OneToOneField('CustomReportTest', on_delete=models.CASCADE)
