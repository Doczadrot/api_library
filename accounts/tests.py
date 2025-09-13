from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from core.models import User


class AuthTests(APITestCase):
    def test_user_can_register(self):
        """
        Тестирует успешную регистрацию пользователя с email и подтверждением пароля.
        """
        # Данные для регистрации нового пользователя
        data = {
            'username': 'testuser',
            'email': 'test@example.com',  # Добавлено поле email
            'password': 'strong_password123',
            'password2': 'strong_password123'
        }
        # Отправляем POST-запрос на эндпоинт регистрации
        response = self.client.post("/api/auth/registration/", data, format='json')

        # Проверяем, что ответ имеет статус 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Проверяем, что пользователь был создан в базе данных
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')

    def test_registration_fails_on_password_mismatch(self):
        """
        Тестирует, что регистрация не удаётся, если пароли не совпадают.
        """
        data = {
            'username': 'testuser2',
            'email': 'test2@example.com',
            'password': 'password_1',
            'password2': 'password_2'  # Несовпадающие пароли
        }
        response = self.client.post("/api/auth/registration/", data, format='json')

        # Ожидаем статус 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Проверяем, что пользователь не был создан
        self.assertEqual(User.objects.count(), 0)

    def test_user_can_obtain_jwt_token(self):
        """
        Тестирует получение JWT-токена после успешной регистрации.
        """
        # Сначала создаем пользователя напрямую в базе данных
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='strong_password123'
        )

        # Данные для получения токена (имя пользователя и пароль)
        data = {
            'username': 'testuser',
            'password': 'strong_password123'
        }
        # Отправляем POST-запрос на эндпоинт получения токена
        response = self.client.post(reverse('token_obtain_pair'), data, format='json')

        # Проверяем, что ответ имеет статус 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что в ответе есть токены access и refresh
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
