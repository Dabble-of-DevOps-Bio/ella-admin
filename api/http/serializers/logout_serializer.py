from rest_framework import serializers
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


class LogoutSerializer(serializers.Serializer):
    token = ''
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']

        return super().validate(attrs)

    def save(self, *args, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            raise InvalidToken

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
