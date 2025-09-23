from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator


class Librarian(models.Model):
    """
    Модель библиотекаря в системе управления библиотекой.
    
    Представляет сотрудника библиотеки, который имеет расширенные права
    для управления книгами, выдачами и читателями. Каждый библиотекарь
    связан с базовой моделью User и имеет уникальный код сотрудника.
    
    Attributes:
        user (ForeignKey): Связь с базовой моделью пользователя (User)
        staff_code (CharField): Уникальный код сотрудника для идентификации
    
    Methods:
        __str__(): Возвращает строковое представление библиотекаря
    """
    # Связь с базовой моделью пользователя (один к одному)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        help_text="Связанный пользователь системы"
    )
    
    # Код сотрудника с валидацией формата
    staff_code = models.CharField(
        max_length=8,
        unique=True,
        verbose_name="Код сотрудника",
        help_text="Уникальный код сотрудника (например: LIB00001)",
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{3}\d{5}$',
                message='Код должен быть в формате: 3 заглавные буквы + 5 цифр'
            )
        ]
    )

    def __str__(self):
        """
        Возвращает строковое представление библиотекаря.
        
        Returns:
            str: Строка в формате "Библиотекарь: username (staff_code)"
        """
        return f"Библиотекарь: {self.user.username} ({self.staff_code})"
    
    class Meta:
        verbose_name = "Библиотекарь"
        verbose_name_plural = "Библиотекари"
        # Индекс для быстрого поиска по коду сотрудника
        indexes = [
            models.Index(fields=['staff_code']),
        ]


class Member(models.Model):
    """
    Модель читателя библиотеки.
    
    Представляет обычного пользователя библиотеки, который может
    брать книги в аренду. Каждый читатель связан с базовой моделью User
    и имеет уникальный код читательского билета.
    
    Attributes:
        user (OneToOneField): Связь с базовой моделью пользователя
        membership_code (CharField): Уникальный код читательского билета
    
    Methods:
        __str__(): Возвращает строковое представление читателя
        get_active_borrowings(): Возвращает активные выдачи читателя
    """
    # Связь с базовой моделью пользователя (один к одному)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        help_text="Связанный пользователь системы"
    )
    
    # Код читательского билета с валидацией
    membership_code = models.CharField(
        max_length=8,
        unique=True,
        verbose_name="Код читателя",
        help_text="Уникальный код читательского билета (например: MEM00001)",
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{3}\d{5}$',
                message='Код должен быть в формате: 3 заглавные буквы + 5 цифр'
            )
        ]
    )

    def __str__(self):
        """
        Возвращает строковое представление читателя.
        
        Returns:
            str: Строка в формате "Читатель: username (membership_code)"
        """
        return f"Читатель: {self.user.username} ({self.membership_code})"
    
    def get_active_borrowings(self):
        """
        Возвращает активные выдачи книг для данного читателя.
        
        Returns:
            QuerySet: Набор активных выдач (BorrowedBook без даты возврата)
        """
        return self.borrowedbook_set.filter(due_date__isnull=False)
    
    class Meta:
        verbose_name = "Читатель"
        verbose_name_plural = "Читатели"
        # Индекс для быстрого поиска по коду читателя
        indexes = [
            models.Index(fields=['membership_code']),
        ]
