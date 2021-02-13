from api.models import UserGroup
from django.db import migrations
from django.db.migrations import migration


def add_inactive_group(*args, **kwargs):
    UserGroup.objects.get_or_create(name='inactive')


class Migration(migration.Migration):
    dependencies = [
        ('api', '0015_variant_report')
    ]

    operations = [
        migrations.RunPython(add_inactive_group)
    ]
