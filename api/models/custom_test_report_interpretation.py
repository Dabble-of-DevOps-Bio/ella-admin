from django.db import models
from django.db.models import OneToOneField


class CustomTestReportInterpretation(models.Model):
    class Meta:
        db_table = 'custom_test_report_interpretation'

    interpretation = models.TextField()

    custom_test_report = OneToOneField('CustomTestReport', on_delete=models.CASCADE)
