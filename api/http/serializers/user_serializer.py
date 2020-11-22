from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.fields import CharField, EmailField
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import PasswordField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.fields.user_auth_group_serializer import UserAuthGroup
from api.http.serializers.user_group_serializer import UserGroupSerializer
from api.models import User, UserGroup


class UserSerializer(BaseModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'username', 'email', 'password', 'new_password', 'group', 'auth_group',
            'created_at', 'updated_at',
        )
        expandable_fields = {
            'group': UserGroupSerializer,
        }

    first_name = CharField(required=True)
    last_name = CharField(required=True)
    username = CharField(required=True, validators=[
        UniqueValidator(queryset=User.objects.all(), message=_('A user with this username already exists.')),
        UniqueValidator(queryset=User.deleted_objects.all(),
                        message=_('This account was recently deleted, please contact a company admin to restore.'))
    ])
    email = EmailField(required=True, validators=[
        UniqueValidator(queryset=User.objects.all(), message=_('A user with this email already exists.')),
        UniqueValidator(queryset=User.deleted_objects.all(),
                        message=_('This account was recently deleted, please contact a company admin to restore.'))
    ])
    password = PasswordField(required=False)
    new_password = CharField(required=False)
    group = serializers.PrimaryKeyRelatedField(required=True, queryset=UserGroup.objects.all())
    auth_group = UserAuthGroup(required=True, queryset=Group.objects.all())

    default_error_messages = {
        'new_password_not_exists': _('Please fill previous password'),
        'invalid_old_password': _('Not valid password'),
        'password_not_exists': _('Please fill previous password')
    }

    def create(self, validated_data):
        user = User(**self.__exclude_fields_for_creation(validated_data))

        if 'password' in validated_data:
            user.set_password(validated_data['password'])

        self.__add_auth_group_advantages(user, validated_data['auth_group'])

        user.save()
        user.auth_groups.set([validated_data['auth_group']])

        return user

    def update(self, instance, validated_data):
        self.__set_password(validated_data)
        self.__set_group(validated_data)

        return super().update(instance, validated_data)

    def validate(self, data):
        def valid_user_password(password: str) -> bool:
            return self.instance.check_password(password)

        if 'method' in self.context and self.context['method'] == 'PUT':
            if ('new_password' in data) and ('password' not in data):
                self.non_field_fail('password', 'password_not_exists')

            if ('password' in data) and ('new_password' not in data):
                self.non_field_fail('new_password', 'new_password_not_exists')

            if ('password' in data) and not valid_user_password(data['password']):
                self.non_field_fail('password', 'invalid_old_password')

            if ('password' in data) and ('new_password' in data):
                validate_password(data['new_password'], self.instance)

        return data

    def __set_password(self, validated_data):
        if 'password' in validated_data:
            self.instance.set_password(validated_data['new_password'])
            self.instance.save()

            del validated_data['password']
            del validated_data['new_password']

    def __set_group(self, validated_data):
        if 'auth_group' in validated_data:
            self.__add_auth_group_advantages(self.instance, validated_data['auth_group'])
            self.instance.auth_groups.set([validated_data['auth_group']])

            del validated_data['auth_group']

    def __exclude_fields_for_creation(self, data: dict) -> dict:
        excluding_fields = ['new_password', 'auth_group']

        return {field_name: value for field_name, value in data.items() if field_name not in excluding_fields}

    def __add_auth_group_advantages(self, user: User, auth_group_id: int) -> None:
        if auth_group_id == User.Group.ADMIN.value:
            user.is_superuser = True
            user.is_staff = True

        if auth_group_id == User.Group.STAFF.value:
            user.is_superuser = False
            user.is_staff = True
