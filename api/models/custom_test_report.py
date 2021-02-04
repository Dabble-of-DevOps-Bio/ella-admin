from django.db import models
from django.db.models import ForeignKey

from api.models.base_model import BaseModel


class CustomTestReport(BaseModel):
    class Meta:
        db_table = 'custom_test_report'

    comments = models.TextField(blank=True)

    custom_test = ForeignKey('CustomTest', on_delete=models.CASCADE)

