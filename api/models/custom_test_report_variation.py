from django.db import models
from django.db.models import ForeignKey


class CustomTestReportVariation(models.Model):
    class Meta:
        db_table = 'custom_test_report_variation'

    description = models.TextField()

    custom_test_report = ForeignKey('CustomTestReport', on_delete=models.CASCADE)
    custom_test_variation = ForeignKey('CustomTestVariation', on_delete=models.CASCADE)
