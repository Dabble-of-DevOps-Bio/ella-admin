from django.db import models
from django.db.models import ForeignKey


class CustomTestGene(models.Model):
    class Meta:
        db_table = 'custom_test_gene'

    name = models.CharField(max_length=255)
    transcript = models.CharField(max_length=255)

    custom_test = ForeignKey('CustomTest', on_delete=models.CASCADE)
