from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework import response, decorators, permissions, status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserCreateSerializer
from drf_yasg.utils import swagger_auto_schema

User = get_user_model()


class RegistrationView(APIView):
    authentication_classes = []
    permission_classes = ()

    @swagger_auto_schema(
        request_body=UserCreateSerializer,
    )
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return response.Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        res = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        return response.Response(res, status.HTTP_201_CREATED)
