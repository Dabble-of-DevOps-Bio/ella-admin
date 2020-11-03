from django.contrib.auth.models import Group
from django.db import migrations
from django.db.migrations import migration


def add_default_groups(*args, **kwargs):
    Group.objects.get_or_create(name='admin')
    Group.objects.get_or_create(name='staff')


class Migration(migration.Migration):
    dependencies = [
        ('api', '0002_auto_20201102_1357')
    ]

    operations = [
        migrations.RunPython(add_default_groups)
    ]
