from django.contrib.auth import password_validation
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'phone_number', 'first_name', 'last_name', 'last_login', 'date_joined', 'password')
        read_only_fields = ('date_joined', 'last_login')

    def create(self, validated_data):
        try:
            password = validated_data.pop('password')
        except Exception as error:
            raise serializers.ValidationError({"status": False, "message": error.__str__()})

        phone_number = validated_data['phone_number']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']

        if User.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError({
                "status": False,
                "message": "phone number already exists for another user."
            })

        try:
            password_validation.validate_password(password=password)
        except Exception as error:
            raise serializers.ValidationError({"status": False, "message": error.__str__()})

        user = User(
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            username=phone_number,
        )
        user.set_password(password)
        user.is_active = True
        user.is_verified = True
        user.save()

        return user


class PasswordChangeSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(max_length=50, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'password', 'new_password')
        extra_kwargs = {'password': {'write_only': True}, 'id': {'read_only': True},
                        'new_password': {'write_only': True}}
