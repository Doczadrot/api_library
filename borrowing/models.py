from datetime import date, timedelta
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


class BorrowedBook(models.Model):
    """
    Модель выдачи книги читателю.
    
    Основная модель для управления выдачами книг в библиотечной системе.
    Связывает конкретный экземпляр книги с читателем и контролирует сроки возврата.
    
    Attributes:
        book_item (OneToOneField): Выданный экземпляр книги
        borrower (ForeignKey): Читатель, взявший книгу
        borrowed_date (DateField): Дата выдачи книги
        due_date (DateField): Плановая дата возврата
        
    Methods:
        is_due_date_past(): Проверяет, просрочена ли выдача
        how_many_days_past_from_due_date(): Количество дней просрочки
        extend_due_date(days): Продлевает срок возврата
        is_overdue(): Проверяет просрочку (алиас для is_due_date_past)
        get_fine_amount(): Рассчитывает размер штрафа за просрочку
    """
    
    # Связь один-к-одному с экземпляром книги (один экземпляр может быть выдан только одному читателю)
    book_item = models.OneToOneField(
        "library.BookItem",
        on_delete=models.CASCADE,
        verbose_name="Экземпляр книги",
        help_text="Конкретный экземпляр книги, который выдается читателю",
        related_name="borrowedbook"
    )
    
    # Связь с читателем библиотеки
    borrower = models.ForeignKey(
        "accounts.Member",
        on_delete=models.CASCADE,
        verbose_name="Читатель",
        help_text="Читатель, который взял книгу",
        related_name="borrowed_books"
    )
    
    # Дата выдачи книги (устанавливается автоматически)
    borrowed_date = models.DateField(
        auto_now_add=True,
        verbose_name="Дата выдачи",
        help_text="Дата, когда книга была выдана читателю"
    )
    
    # Планируемая дата возврата
    due_date = models.DateField(
        validators=[MinValueValidator(date.today)],
        verbose_name="Дата возврата",
        help_text="Планируемая дата возврата книги"
    )

    def clean(self):
        """
        Валидация модели перед сохранением.
        
        Raises:
            ValidationError: Если дата возврата раньше даты выдачи
        """
        super().clean()
        if self.due_date and self.borrowed_date and self.due_date < self.borrowed_date:
            raise ValidationError(
                "Дата возврата не может быть раньше даты выдачи"
            )

    def is_due_date_past(self):
        """
        Проверяет, просрочена ли выдача книги.
        
        Returns:
            bool: True, если срок возврата истек
        """
        return self.due_date < date.today()
    
    def is_overdue(self):
        """
        Алиас для is_due_date_past() для лучшей читаемости кода.
        
        Returns:
            bool: True, если выдача просрочена
        """
        return self.is_due_date_past()

    def how_many_days_past_from_due_date(self):
        """
        Вычисляет количество дней просрочки.
        
        Returns:
            int or None: Количество дней просрочки или None, если не просрочена
        """
        time_delta = date.today() - self.due_date
        if time_delta.days >= 0:
            return time_delta.days
        return None
    
    def extend_due_date(self, days: int):
        """
        Продлевает срок возврата книги на указанное количество дней.
        
        Args:
            days (int): Количество дней для продления
            
        Raises:
            ValueError: Если передано отрицательное количество дней
        """
        if days < 0:
            raise ValueError("Количество дней для продления должно быть положительным")
            
        self.due_date += timedelta(days=days)
        self.save(update_fields=['due_date'])
    
    def get_fine_amount(self, daily_fine: float = 10.0):
        """
        Рассчитывает размер штрафа за просрочку.
        
        Args:
            daily_fine (float): Размер штрафа за один день просрочки
            
        Returns:
            float: Общий размер штрафа или 0, если просрочки нет
        """
        overdue_days = self.how_many_days_past_from_due_date()
        if overdue_days:
            return overdue_days * daily_fine
        return 0.0

    def __str__(self):
        """
        Возвращает строковое представление выдачи книги.
        
        Returns:
            str: Строка в формате "Выдача: название книги → имя читателя (срок до даты)"
        """
        status = " [ПРОСРОЧЕНО]" if self.is_overdue() else ""
        return (
            f"Выдача: {self.book_item.book.title} → "
            f"{self.borrower.user.username} (до {self.due_date}){status}"
        )

    class Meta:
        verbose_name = "Выдача книги"
        verbose_name_plural = "Выдачи книг"
        # Сортировка по дате возврата (просроченные в начале)
        ordering = ['due_date', 'borrowed_date']
        # Индексы для оптимизации запросов
        indexes = [
            models.Index(fields=['due_date']),
            models.Index(fields=['borrowed_date']),
            models.Index(fields=['borrower']),
        ]
        # Ограничения на уровне базы данных
        constraints = [
            models.CheckConstraint(
                check=models.Q(due_date__gte=models.F('borrowed_date')),
                name='due_date_after_borrowed_date'
            )
        ]
