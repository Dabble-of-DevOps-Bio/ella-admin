from django.db import models
from django.db.models import OneToOneField


class CustomReportInterpretation(models.Model):
    class Meta:
        db_table = 'custom_report_interpretation'

    interpretations = models.TextField()

    custom_report_result = OneToOneField('CustomReportResult', on_delete=models.CASCADE)
