from django.conf import settings
from rest_framework import status
from django.http import HttpResponse
from rest_framework import permissions
from rest_framework.generics import GenericAPIView

from api.http.serializers import StaffAppLoginSerializer


class StaffAppLoginView(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = StaffAppLoginSerializer

    def post(self, request):
        serializer = self.get_serializer()
        session, token = serializer.create_staff_app_user_session(request.user)

        response = HttpResponse(status=status.HTTP_302_FOUND)
        response.set_cookie(key='AuthenticationToken',
                            value=token,
                            expires=session.expires, domain=settings.FRONTEND_DOMAIN, path='/', httponly=True)

        return response
