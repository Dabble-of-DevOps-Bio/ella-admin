from django.db import models
from django.db.models import OneToOneField


class CustomReportInterpretation(models.Model):
    class Meta:
        db_table = 'custom_report_interpretation'

    interpretation = models.TextField()

    custom_report_test = OneToOneField('CustomReportTest', on_delete=models.CASCADE)
