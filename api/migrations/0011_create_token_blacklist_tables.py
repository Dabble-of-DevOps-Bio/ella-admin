# Generated by Django 3.0.10 on 2020-11-02 13:21

from django.db import migrations, connection
from django.conf import settings


def create_token_blacklist_outstandingtoken(*args, **kwargs):
    if settings.ENV != 'testing':
        with connection.cursor() as cursor:
            cursor.execute(
                'create table token_blacklist_outstandingtoken('
                    'id         serial                   not null constraint token_blacklist_outstandingtoken_pkey primary key,'
                    'token      text                     not null,'
                    'created_at timestamp with time zone,'
                    'expires_at timestamp with time zone not null,'
                    'user_id    integer constraint token_blacklist_outs_user_id_83bc629a_fk_auth_user references \"user\" deferrable initially deferred,'
                    'jti        varchar(255)             not null constraint token_blacklist_outstandingtoken_jti_hex_d9bdf6f7_uniq unique'
                ')'
            )

            cursor.execute('alter table token_blacklist_outstandingtoken owner to postgres')

            cursor.execute('create index token_blacklist_outstandingtoken_jti_hex_d9bdf6f7_like on token_blacklist_outstandingtoken (jti)')

            cursor.execute('create index token_blacklist_outstandingtoken_user_id_83bc629a on token_blacklist_outstandingtoken (user_id)')

def create_token_blacklist_blacklistedtoken(*args, **kwargs):
    if settings.ENV != 'testing':
        with connection.cursor() as cursor:
            cursor.execute(
                'create table token_blacklist_blacklistedtoken('
                    'id serial not null constraint token_blacklist_blacklistedtoken_pkey primary key,'
                    'blacklisted_at timestamp with time zone not null,'
                    'token_id integer not null constraint token_blacklist_blacklistedtoken_token_id_key unique constraint token_blacklist_blac_token_id_3cc7fe56_fk_token_bla references token_blacklist_outstandingtoken deferrable initially deferred'
                ')'
            )

            cursor.execute('alter table token_blacklist_blacklistedtoken owner to postgres')


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_create_django_rest_passwordreset_resetpasswordtoken'),
    ]

    operations = [
        migrations.RunPython(create_token_blacklist_outstandingtoken),
        migrations.RunPython(create_token_blacklist_blacklistedtoken),
    ]
