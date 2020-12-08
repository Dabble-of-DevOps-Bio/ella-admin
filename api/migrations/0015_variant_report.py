# Generated by Django 3.0.10 on 2020-11-02 13:21

from django.db import migrations, connection


def create_django_admin_log(*args, **kwargs):
    with connection.cursor() as cursor:
        cursor.execute(
            'create table variantreport('
                'id serial not null constraint variant_reports_pkey primary key,'
                'created_at timestamp with time zone not null,'
                'updated_at timestamp with time zone not null,'
                'data       jsonb                    not null,'
                'comment    varchar(255)             not null,'
                'literature varchar(255)             not null,'
                'user_id integer not null constraint fk_variantreport_user_id_user references "user",'
                'analysis_id integer not null constraint fk_variantreport_analysis_id_analysis references analysis,'
                'analysis_interpretation_id integer not null constraint fk_variantreport_analysis_interpretation_id_analysis_interpretation references analysisinterpretation'
            ')'
        )

        cursor.execute('alter table variantreport owner to postgres')


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0014_update_usergrpoupgenepanel_table'),
    ]

    operations = [
        migrations.RunPython(create_django_admin_log),
    ]