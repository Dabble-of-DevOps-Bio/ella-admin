from django.db import models
from django.db.models import OneToOneField


class CustomReportResult(models.Model):
    class Meta:
        db_table = 'custom_report_result'

    result = models.TextField()

    custom_report_variation = OneToOneField('CustomReportVariation', on_delete=models.CASCADE)
