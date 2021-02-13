import datetime

import pytz
from rest_framework import serializers

from api.models import UserSession
from api.utilities.user import generate_user_session_token


class StaffAppLoginSerializer(serializers.Serializer):

    def validate(self, attrs):
        pass

    def save(self, *args, **kwargs):
        pass

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def create_staff_app_user_session(self, user):
        token, hashed_token = generate_user_session_token()

        user_session = UserSession(
            token=hashed_token,
            user_id=user.pk,
            issued=datetime.datetime.now(pytz.utc),
            expires=user.password_expiry,
        )
        user_session.save()

        return user_session, token
