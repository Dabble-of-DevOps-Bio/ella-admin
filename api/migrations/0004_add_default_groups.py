from django.contrib.auth.models import Group
from django.db import migrations
from django.db.migrations import migration


def add_auth_groups(*args, **kwargs):
    Group.objects.get_or_create(name='admin')
    Group.objects.get_or_create(name='staff')


class Migration(migration.Migration):
    dependencies = [
        ('api', '0003_create_user_permissions_table')
    ]

    operations = [
        migrations.RunPython(add_auth_groups)
    ]
