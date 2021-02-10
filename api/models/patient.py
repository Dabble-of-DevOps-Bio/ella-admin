from django.db import models
from django.db.models import CharField
from django.db.models import DateField, DateTimeField
from django.utils.translation import gettext_lazy as _


class Patient(models.Model):
    class Gender(models.TextChoices):
        MALE = "MALE", _('Male')
        FEMALE = "FEMALE", _('Female')

    class Meta:
        db_table = 'patient'

    name = CharField(max_length=255)
    birthday = DateField()
    gender = models.CharField(max_length=255, choices=Gender.choices, default=Gender.MALE.value)

    sample_type = CharField(max_length=255, blank=True)
    sample_id = CharField(max_length=255, blank=True)

    test_accession = CharField(max_length=255, blank=True)
    test_ordered = CharField(max_length=255, blank=True)
    test_code = CharField(max_length=255, blank=True)

    ordered_by = CharField(max_length=255, blank=True)

    sample_collection_date = DateTimeField(blank=True)
    sample_accession_date = DateTimeField(blank=True)
    report_date = DateTimeField(blank=True)
