from django.contrib.auth import authenticate
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt import tokens
from rest_framework import generics, permissions, serializers, response, viewsets, views, status

from apis.helpers.authentication import BasicAuth
from apis.users.models import User
from apis.users.serializers import PasswordChangeSerializer, UserSerializer


# Create your views here.

class UserOnboarding(viewsets.ModelViewSet):
    http_method_names = ['post', 'options']
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'
    authentication_classes = [BasicAuth]
    permission_classes = [AllowAny,]

    def perform_create(self, serializer):
        return serializer.save()


class UserDetailsAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = self.request.user
        serializer = UserSerializer(user)
        data = {
            "status": True,
            "message": "success",
            "data": serializer.data
        }
        return response.Response(data, status=status.HTTP_200_OK)


class UserLoginView(views.APIView):
    authentication_classes = [BasicAuth]
    permission_classes = [AllowAny,]
    http_method_names = ['post', ]

    @staticmethod
    def post(request):
        try:
            phone_number = request.data["phone_number"]
            password = request.data["password"]
        except KeyError as e:
            raise serializers.ValidationError({
                "status": False,
                "message": f"{e} is required"
            })

        try:
            user_object = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'status': False,
                'message': "Invalid credentials"
            })

        except Exception as err:
            raise serializers.ValidationError({
                'status': False,
                'message': err
            })

        user: User | AbstractBaseUser = authenticate(username=user_object.username, password=password)
        if not user:
            raise serializers.ValidationError({
                'status': False,
                'message': "Invalid credentials"
            })

        user.last_login = timezone.now()
        token = tokens.AccessToken.for_user(user)
        user.save()

        return response.Response(
            {
                "status": True,
                "message": "success",
                "data": {
                    "token": str(token),
                    "id": user.id,
                    "phone_number": user.phone_number,
                    "full_name": user.get_full_name(),
                    "verified": user.is_verified,
                },
                "errors": "null",
            },
            status=status.HTTP_200_OK,
        )


class PasswordChangeAPIView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['patch', 'options']
    serializer_class = PasswordChangeSerializer
    queryset = User.objects.all()
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        user = self.request.user
        try:
            if not user.check_password(self.request.data["old_password"]):
                raise serializers.ValidationError({
                    'status': False,
                    'message': 'Your old password is incorrect'
                })
        except Exception as error:  # noqa
            raise serializers.ValidationError({
                'status': False,
                'message': 'Your old password is incorrect'
            })
        try:
            validate_password(self.request.data["new_password"])
        except Exception as error:
            raise serializers.ValidationError({
                'status': False,
                'message': error
            })
        try:
            user.set_password(self.request.data["new_password"])
            user.save()
        except Exception as error:
            raise serializers.ValidationError({
                'status': False,
                'message': error
            })
        return response.Response({
            'status': True,
            'message': "Password has been changed successfully"
        })
