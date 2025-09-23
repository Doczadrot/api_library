from dj_rest_auth.registration.views import RegisterView
from rest_framework.response import Response
from rest_framework import status

from .serializers import CustomRegisterSerializer


class CustomRegisterView(RegisterView):
    """
    Кастомное представление для регистрации пользователей.
    
    Расширяет стандартное RegisterView из dj-rest-auth для
    поддержки собственной логики валидации и регистрации.
    
    Features:
        - Использует CustomRegisterSerializer для валидации
        - Поддерживает гибкую обработку полей паролей
        - Интегрируется с системой JWT аутентификации
        - Автоматически создает JWT токены при успешной регистрации
        
    Request Format:
        POST /api/auth/registration/
        {
            "username": "string",
            "email": "email@example.com", 
            "password": "string",
            "password2": "string"
        }
        
    Response Format:
        201 Created:
        {
            "access_token": "jwt_access_token",
            "refresh_token": "jwt_refresh_token", 
            "user": {
                "id": 1,
                "username": "string",
                "email": "email@example.com"
            }
        }
        
        400 Bad Request:
        {
            "password": ["Пароли не совпадают."],
            "email": ["Пользователь с таким email уже существует."]
        }
        
    Note:
        Этот view автоматически интегрируется с dj-rest-auth
        и системой JWT токенов, настроенной в settings.py.
    """
    # Используем кастомный сериализатор для регистрации
    serializer_class = CustomRegisterSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Создание нового пользователя с улучшенной обработкой ошибок.
        
        Args:
            request: HTTP запрос с данными регистрации
            
        Returns:
            Response: Ответ с токенами и данными пользователя или ошибками валидации
        """
        # Вызываем родительский метод создания
        response = super().create(request, *args, **kwargs)
        
        # Добавляем дополнительную информацию в успешный ответ
        if response.status_code == status.HTTP_201_CREATED:
            response.data['message'] = 'Пользователь успешно зарегистрирован'
            
        return response


