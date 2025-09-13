from django.contrib.auth import get_user_model
from rest_framework import serializers
from typing import Any, Dict
from dj_rest_auth.registration.serializers import RegisterSerializer

from ..models import Librarian, Member

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения/отображения данных пользователя.
    Не содержит пароль.
    """
    class Meta:
        model = User
        fields = ("id", "username", "email")


class UserCreationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания пользователя.
    Используется для регистрации.
    """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ("username", "email", "password", "password2")

    def validate(self, data):
        """Проверяет, что пароли совпадают."""
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)


class MemberSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения данных Member.
    """
    user = UserSerializer()

    class Meta:
        model = Member
        fields = ("id", "membership_code", "user")


class CreateMemberSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания Member.
    Создает пользователя и связывает его с Member.
    """
    user = UserCreationSerializer()

    class Meta:
        model = Member
        fields = ("user",)

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user = User.objects.create_user(**user_data)
        member = Member.objects.create(user=user)
        return member


class LibrarianSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения данных Librarian.
    """
    user = UserSerializer()

    class Meta:
        model = Librarian
        fields = ("id", "staff_code", "user")


class CreateLibrarianSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания Librarian.
    Создает пользователя и связывает его с Librarian.
    """
    user = UserCreationSerializer()

    class Meta:
        model = Librarian
        fields = ("user",)

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user = User.objects.create_user(**user_data)
        librarian = Librarian.objects.create(user=user)
        return librarian


class CustomRegisterSerializer(RegisterSerializer):
    """
    Кастомный сериализатор регистрации для dj-rest-auth"""

    password1 = serializers.CharField(write_only=True, required=False, style={"input_type": "password"})
    password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})
    password2 = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})

    def validate(self, attrs: Dict[str, Any]):
        password = attrs.get("password") or attrs.get("password1")
        password_confirm = attrs.get("password2")

        if not password or not password_confirm:
            raise serializers.ValidationError({"password": "Пароль и подтверждение обязательны."})

        if password != password_confirm:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})

        attrs["password1"] = password
        attrs["password2"] = password_confirm

        return super().validate(attrs)

    def get_cleaned_data(self):
        cleaned = super().get_cleaned_data()
        if not cleaned.get("password1") and self.validated_data.get("password"):
            cleaned["password1"] = self.validated_data.get("password")
        return cleaned
