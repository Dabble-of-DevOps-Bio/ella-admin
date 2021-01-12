from django.db import models
from django.db.models import OneToOneField


class CustomReportFullReport(models.Model):
    class Meta:
        db_table = 'custom_report_full_report'

    patient_id = models.IntegerField(null=True)
    report_text = models.TextField(blank=True)
    time_submitted = models.DateTimeField(blank=True)

    custom_report_test = OneToOneField('CustomReportTest', on_delete=models.CASCADE)
