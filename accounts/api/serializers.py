from django.contrib.auth import get_user_model
from rest_framework import serializers
from typing import Any, Dict
from dj_rest_auth.registration.serializers import RegisterSerializer

from ..models import Librarian, Member

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для безопасного отображения данных пользователя.
    
    Используется для чтения и отображения информации о пользователе
    в API ответах. Исключает конфиденциальные поля типа пароля.
    
    Fields:
        id (int): Уникальный идентификатор пользователя
        username (str): Имя пользователя
        email (str): Email адрес пользователя
        
    Note:
        Пароль и другие чувствительные данные намеренно исключены
        из сериализации для безопасности.
    """
    class Meta:
        model = User
        fields = ("id", "username", "email")
        read_only_fields = ("id",)  # ID всегда только для чтения


class UserCreationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания нового пользователя с валидацией паролей.
    
    Обеспечивает безопасное создание пользователей с подтверждением пароля.
    Используется при регистрации новых пользователей в системе.
    
    Fields:
        username (str): Уникальное имя пользователя
        email (str): Уникальный email адрес
        password (str): Пароль пользователя (только для записи)
        password2 (str): Подтверждение пароля (только для записи)
        
    Validation:
        - Проверяет совпадение password и password2
        - Применяет стандартные валидаторы Django для паролей
        
    Returns:
        User: Созданный экземпляр пользователя
    """
    # Поле для основного пароля
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Пароль пользователя"
    )
    
    # Поле для подтверждения пароля
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Подтверждение пароля (должно совпадать с основным)"
    )

    class Meta:
        model = User
        fields = ("username", "email", "password", "password2")
        extra_kwargs = {
            'email': {'required': True},  # Email обязателен
            'username': {'required': True}  # Username обязателен
        }

    def validate(self, data):
        """
        Валидация данных пользователя.
        
        Проверяет совпадение основного пароля и подтверждения.
        
        Args:
            data (dict): Данные для валидации
            
        Returns:
            dict: Валидированные данные
            
        Raises:
            ValidationError: Если пароли не совпадают
        """
        if data['password'] != data['password2']:
            raise serializers.ValidationError({
                "password": "Пароли не совпадают."
            })
        return data

    def create(self, validated_data):
        """
        Создание нового пользователя.
        
        Удаляет поле подтверждения пароля и создает пользователя
        с хешированием пароля через create_user().
        
        Args:
            validated_data (dict): Валидированные данные
            
        Returns:
            User: Созданный пользователь
        """
        # Удаляем поле подтверждения пароля перед созданием
        validated_data.pop('password2')
        # Используем create_user для правильного хеширования пароля
        return User.objects.create_user(**validated_data)


class MemberSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения информации о читателе библиотеки.
    
    Предоставляет полную информацию о читателе, включая
    вложенные данные пользователя. Используется для чтения данных.
    
    Fields:
        id (int): Уникальный идентификатор читателя
        membership_code (str): Код читательского билета
        user (UserSerializer): Вложенная информация о пользователе
        
    Note:
        Данный сериализатор предназначен только для чтения.
        Для создания читателей используйте CreateMemberSerializer.
    """
    # Вложенный сериализатор для отображения данных пользователя
    user = UserSerializer(read_only=True)

    class Meta:
        model = Member
        fields = ("id", "membership_code", "user")
        read_only_fields = ("id", "membership_code")  # Код генерируется автоматически


class CreateMemberSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания нового читателя библиотеки.
    
    Создает пользователя и связанную с ним запись читателя
    в рамках одной транзакции. Автоматически генерирует
    код читательского билета.
    
    Fields:
        user (UserCreationSerializer): Данные нового пользователя
        
    Process:
        1. Валидирует данные пользователя
        2. Создает пользователя с хешированным паролем
        3. Создает запись читателя, связанную с пользователем
        4. Генерирует уникальный код читательского билета
        
    Returns:
        Member: Созданный читатель с связанным пользователем
    """
    # Вложенный сериализатор для создания пользователя
    user = UserCreationSerializer()

    class Meta:
        model = Member
        fields = ("user",)

    def create(self, validated_data):
        """
        Создание читателя с автоматической генерацией кода.
        
        Args:
            validated_data (dict): Валидированные данные
            
        Returns:
            Member: Созданный читатель
            
        Note:
            Код читательского билета генерируется автоматически
            в формате MEM{id:05d} после создания записи.
        """
        # Извлекаем данные пользователя
        user_data = validated_data.pop("user")
        # Удаляем поле подтверждения пароля
        user_data.pop('password2', None)
        # Создаем пользователя
        user = User.objects.create_user(**user_data)
        # Создаем читателя
        member = Member.objects.create(user=user)
        # Генерируем код читательского билета
        member.membership_code = f"MEM{member.id:05d}"
        member.save(update_fields=['membership_code'])
        return member


class LibrarianSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения информации о библиотекаре.
    
    Предоставляет полную информацию о библиотекаре, включая
    вложенные данные пользователя. Используется для чтения данных.
    
    Fields:
        id (int): Уникальный идентификатор библиотекаря
        staff_code (str): Код сотрудника библиотеки
        user (UserSerializer): Вложенная информация о пользователе
        
    Note:
        Данный сериализатор предназначен только для чтения.
        Для создания библиотекарей используйте CreateLibrarianSerializer.
    """
    # Вложенный сериализатор для отображения данных пользователя
    user = UserSerializer(read_only=True)

    class Meta:
        model = Librarian
        fields = ("id", "staff_code", "user")
        read_only_fields = ("id", "staff_code")  # Код генерируется автоматически


class CreateLibrarianSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания нового библиотекаря.
    
    Создает пользователя и связанную с ним запись библиотекаря
    в рамках одной транзакции. Автоматически генерирует
    код сотрудника библиотеки.
    
    Fields:
        user (UserCreationSerializer): Данные нового пользователя
        
    Process:
        1. Валидирует данные пользователя
        2. Создает пользователя с хешированным паролем
        3. Создает запись библиотекаря, связанную с пользователем
        4. Генерирует уникальный код сотрудника
        
    Returns:
        Librarian: Созданный библиотекарь с связанным пользователем
        
    Note:
        Только администраторы могут создавать библиотекарей.
    """
    # Вложенный сериализатор для создания пользователя
    user = UserCreationSerializer()

    class Meta:
        model = Librarian
        fields = ("user",)

    def create(self, validated_data):
        """
        Создание библиотекаря с автоматической генерацией кода сотрудника.
        
        Args:
            validated_data (dict): Валидированные данные
            
        Returns:
            Librarian: Созданный библиотекарь
            
        Note:
            Код сотрудника генерируется автоматически
            в формате LIB{id:05d} после создания записи.
        """
        # Извлекаем данные пользователя
        user_data = validated_data.pop("user")
        # Удаляем поле подтверждения пароля
        user_data.pop('password2', None)
        # Создаем пользователя
        user = User.objects.create_user(**user_data)
        # Создаем библиотекаря
        librarian = Librarian.objects.create(user=user)
        # Генерируем код сотрудника
        librarian.staff_code = f"LIB{librarian.id:05d}"
        librarian.save(update_fields=['staff_code'])
        return librarian


class CustomRegisterSerializer(RegisterSerializer):
    """
    Кастомный сериализатор регистрации для интеграции с dj-rest-auth.
    
    Расширяет стандартный RegisterSerializer для поддержки
    собственной логики валидации паролей и совместимости
    с фронтенд-интерфейсом.
    
    Fields:
        username (str): Имя пользователя
        email (str): Email адрес
        password (str): Основной пароль
        password2 (str): Подтверждение пароля
        password1 (str): Альтернативное поле пароля (для совместимости)
        
    Features:
        - Гибкая обработка полей паролей (password/password1)
        - Валидация совпадения паролей
        - Интеграция с системой аутентификации dj-rest-auth
        
    Note:
        Используется автоматически системой dj-rest-auth
        при регистрации новых пользователей через API.
    """
    # Альтернативное поле пароля для совместимости с dj-rest-auth
    password1 = serializers.CharField(
        write_only=True,
        required=False,
        style={"input_type": "password"},
        help_text="Альтернативное поле пароля (для совместимости)"
    )
    
    # Основное поле пароля
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        help_text="Пароль пользователя"
    )
    
    # Подтверждение пароля
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        help_text="Подтверждение пароля"
    )

    def validate(self, attrs: Dict[str, Any]):
        """
        Валидация данных регистрации с гибкой обработкой паролей.
        
        Args:
            attrs (Dict[str, Any]): Данные для валидации
            
        Returns:
            Dict[str, Any]: Валидированные данные
            
        Raises:
            ValidationError: При несовпадении паролей или отсутствии обязательных полей
        """
        # Определяем основной пароль (может быть в поле password или password1)
        password = attrs.get("password") or attrs.get("password1")
        password_confirm = attrs.get("password2")

        # Проверяем наличие обязательных полей
        if not password or not password_confirm:
            raise serializers.ValidationError({
                "password": "Пароль и подтверждение обязательны."
            })

        # Проверяем совпадение паролей
        if password != password_confirm:
            raise serializers.ValidationError({
                "password": "Пароли не совпадают."
            })

        # Устанавливаем стандартные поля для dj-rest-auth
        attrs["password1"] = password
        attrs["password2"] = password_confirm

        # Вызываем родительскую валидацию
        return super().validate(attrs)

    def get_cleaned_data(self):
        """
        Подготовка очищенных данных для создания пользователя.
        
        Обеспечивает совместимость с базовым RegisterSerializer
        и правильную передачу пароля в систему создания пользователя.
        
        Returns:
            Dict[str, Any]: Очищенные данные для создания пользователя
        """
        # Получаем базовые очищенные данные
        cleaned = super().get_cleaned_data()
        
        # Если password1 не установлен, используем password
        if not cleaned.get("password1") and self.validated_data.get("password"):
            cleaned["password1"] = self.validated_data.get("password")
            
        return cleaned
