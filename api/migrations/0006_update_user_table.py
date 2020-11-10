# Generated by Django 3.0.10 on 2020-11-02 13:21

from django.db import migrations, connection


def update_user_table(*args, **kwargs):
    with connection.cursor() as cursor:
        cursor.execute(
            'alter table "user" '
                'ADD COLUMN is_superuser boolean not null default False, '
                'ADD COLUMN is_staff boolean not null default True, '
                'ADD COLUMN date_joined timestamp with time zone not null default now(), '
                'ADD COLUMN last_login timestamp with time zone, '
                'ADD COLUMN created_at timestamp with time zone not null default now(), '
                'ADD COLUMN updated_at timestamp with time zone not null default now(), '
                'ADD COLUMN deleted timestamp with time zone'
        )


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('api', '0005_set_user_auth_group'),
    ]

    operations = [
        migrations.RunPython(update_user_table),
    ]
