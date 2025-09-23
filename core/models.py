from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Кастомная модель пользователя для системы библиотеки.
    
    Расширяет стандартную модель Django User, добавляя уникальное поле email.
    Используется как базовая модель для всех пользователей системы: 
    библиотекарей, читателей и администраторов.
    
    Attributes:
        email (EmailField): Уникальный email адрес пользователя
        username (CharField): Унаследованное имя пользователя
        first_name (CharField): Унаследованное имя
        last_name (CharField): Унаследованная фамилия
        is_staff (BooleanField): Унаследованный флаг администратора
        is_active (BooleanField): Унаследованный флаг активности
        date_joined (DateTimeField): Унаследованная дата регистрации
    """
    # Переопределяем email поле как уникальное для всей системы
    email = models.EmailField(
        unique=True,
        verbose_name="Email адрес",
        help_text="Уникальный email адрес пользователя"
    )

    def __str__(self):
        """
        Возвращает строковое представление пользователя.
        
        Returns:
            str: Строка в формате "username, email"
        """
        return f"{self.username}, {self.email}"
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        # Индекс для ускорения поиска по email
        indexes = [
            models.Index(fields=['email']),
        ]
