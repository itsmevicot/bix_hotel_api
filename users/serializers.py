from datetime import date

from rest_framework import serializers

from users.enums import UserRole
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'cpf', 'birth_date', 'password',]
        extra_kwargs = {
            'role': {'default': UserRole.CLIENT.value}
        }

    @staticmethod
    def validate_birth_date(value):
        age = date.today().year - value.year - ((date.today().month, date.today().day) < (value.month, value.day))
        if age < 18:
            raise serializers.ValidationError("You must be at least 18 years old to register.")
        return value

    @staticmethod
    def validate_email(value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    @staticmethod
    def validate_cpf(value):
        cpf = value.replace(".", "").replace("-", "")
        if User.objects.filter(cpf=cpf).exists():
            raise serializers.ValidationError("This CPF is already in use.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user
