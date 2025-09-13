from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Кастомная модель пользователя
    """
    email = models.EmailField(unique=True)

    def __str__(self):
        """Возвращает строковое представление пользователя."""
        return f"{self.username}, {self.email}"
