from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator


class Author(models.Model):
    """
    Модель автора книг.
    
    Представляет автора произведений в библиотечной системе.
    Один автор может написать множество книг, и одна книга
    может иметь несколько авторов (связь many-to-many).
    
    Attributes:
        name (CharField): Полное имя автора
        description (TextField): Биография или описание автора
        
    Methods:
        __str__(): Возвращает строковое представление автора
        get_books_count(): Возвращает количество книг автора
    """
    # Полное имя автора
    name = models.CharField(
        max_length=255,
        verbose_name="Имя автора",
        help_text="Полное имя автора (Фамилия Имя Отчество)"
    )
    
    # Биография или описание автора
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Описание",
        help_text="Краткая биография или описание автора"
    )

    def __str__(self):
        """
        Возвращает строковое представление автора.
        
        Returns:
            str: Строка в формате "Автор: имя"
        """
        return f"Автор: {self.name}"
    
    def get_books_count(self):
        """
        Возвращает количество книг, написанных автором.
        
        Returns:
            int: Количество книг автора
        """
        return self.books.count()

    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"
        # Сортировка по имени автора
        ordering = ['name']
        # Индекс для быстрого поиска по имени
        indexes = [
            models.Index(fields=['name']),
        ]


class Book(models.Model):
    """
    Модель книги в библиотечной системе.
    
    Представляет информацию о книге как о библиографической единице.
    Одна книга может иметь несколько физических экземпляров (BookItem).
    Связана с авторами через отношение many-to-many.
    
    Attributes:
        title (CharField): Название книги
        isbn (CharField): Уникальный международный номер книги
        author (ManyToManyField): Авторы книги
        subject (CharField): Тематическая категория книги
        page_counts (IntegerField): Количество страниц в книге
        
    Methods:
        __str__(): Возвращает строковое представление книги
        get_available_copies(): Возвращает количество доступных экземпляров
        get_authors_names(): Возвращает имена всех авторов через запятую
    """
    # Название книги
    title = models.CharField(
        max_length=255,
        verbose_name="Название",
        help_text="Полное название книги"
    )
    
    # ISBN номер с валидацией формата
    isbn = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="ISBN",
        help_text="Международный стандартный номер книги",
        validators=[
            RegexValidator(
                regex=r'^(?:ISBN(?:-1[03])?:? )?(?=[0-9X]{10}$|(?=(?:[0-9]+[- ]){3})[- 0-9X]{13}$|97[89][0-9]{10}$|(?=(?:[0-9]+[- ]){4})[- 0-9]{17}$)(?:97[89][- ]?)?[0-9]{1,5}[- ]?[0-9]+[- ]?[0-9]+[- ]?[0-9X]$',
                message='Введите корректный ISBN номер'
            )
        ]
    )
    
    # Связь с авторами (многие ко многим)
    author = models.ManyToManyField(
        Author,
        related_name="books",
        verbose_name="Авторы",
        help_text="Авторы данной книги"
    )
    
    # Тематическая категория
    subject = models.CharField(
        max_length=127,
        verbose_name="Тема",
        help_text="Тематическая категория или жанр книги"
    )
    
    # Количество страниц с валидацией минимального значения
    page_counts = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Количество страниц",
        help_text="Общее количество страниц в книге",
        validators=[MinValueValidator(1, message="Количество страниц должно быть больше 0")]
    )

    def __str__(self):
        """
        Возвращает строковое представление книги.
        
        Returns:
            str: Строка в формате "Книга: название"
        """
        return f"Книга: {self.title}"
    
    def get_available_copies(self):
        """
        Возвращает количество доступных для выдачи экземпляров книги.
        
        Returns:
            int: Количество доступных экземпляров
        """
        return self.book_items.filter(status=BookItem.STATUS_AVAILABLE).count()
    
    def get_authors_names(self):
        """
        Возвращает имена всех авторов книги через запятую.
        
        Returns:
            str: Имена авторов, разделенные запятой
        """
        return ", ".join([author.name for author in self.author.all()])

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        # Сортировка по названию
        ordering = ['title']
        # Индексы для ускорения поиска
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['isbn']),
            models.Index(fields=['subject']),
        ]


class BookItem(models.Model):
    """
    Модель физического экземпляра книги.
    
    Представляет конкретный физический экземпляр книги в библиотеке.
    Каждый экземпляр имеет уникальный штрих-код и статус.
    Одна книга (Book) может иметь множество экземпляров (BookItem).
    
    Attributes:
        book (ForeignKey): Связь с моделью книги
        barcode (CharField): Уникальный штрих-код экземпляра
        status (CharField): Текущий статус экземпляра
        publication_date (DateField): Дата публикации данного издания
        
    Methods:
        is_available(): Проверяет, доступен ли экземпляр для выдачи
        change_status(to): Изменяет статус экземпляра
        can_be_borrowed(): Проверяет, можно ли выдать экземпляр
        get_borrower(): Возвращает текущего держателя книги
    """
    # Константы статусов экземпляра книги
    STATUS_AVAILABLE = "A"      # Доступна для выдачи
    STATUS_BORROWED = "B"       # Выдана читателю  
    STATUS_RESERVED = "R"       # Зарезервирована
    STATUS_LOST = "L"          # Утеряна

    STATUS_CHOICES = (
        (STATUS_AVAILABLE, "Доступна"),
        (STATUS_BORROWED, "Выдана"),
        (STATUS_RESERVED, "Зарезервирована"),
        (STATUS_LOST, "Утеряна"),
    )
    
    # Связь с моделью книги (многие экземпляры к одной книге)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="book_items",
        verbose_name="Книга",
        help_text="Книга, к которой относится данный экземпляр"
    )
    
    # Уникальный штрих-код экземпляра
    barcode = models.CharField(
        max_length=15,
        unique=True,
        verbose_name="Штрих-код",
        help_text="Уникальный штрих-код для идентификации экземпляра",
        validators=[
            RegexValidator(
                regex=r'^[0-9]{13}$',
                message='Штрих-код должен состоять из 13 цифр'
            )
        ]
    )
    
    # Текущий статус экземпляра
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default=STATUS_AVAILABLE,
        verbose_name="Статус",
        help_text="Текущий статус экземпляра книги"
    )
    
    # Дата публикации данного издания
    publication_date = models.DateField(
        verbose_name="Дата публикации",
        help_text="Дата публикации данного издания"
    )

    def is_available(self):
        """
        Проверяет, доступен ли экземпляр для выдачи.
        
        Returns:
            bool: True, если экземпляр доступен для выдачи
        """
        return self.status == self.STATUS_AVAILABLE

    def can_be_borrowed(self):
        """
        Проверяет, можно ли выдать экземпляр читателю.
        
        Returns:
            bool: True, если экземпляр можно выдать
        """
        return self.status in [self.STATUS_AVAILABLE, self.STATUS_RESERVED]

    def change_status(self, to: str):
        """
        Изменяет статус экземпляра книги.
        
        Args:
            to (str): Новый статус из доступных вариантов
            
        Raises:
            ValueError: Если передан недопустимый статус
        """
        valid_statuses = [choice[0] for choice in self.STATUS_CHOICES]
        if to not in valid_statuses:
            raise ValueError(f"Недопустимый статус: {to}")
            
        self.status = to
        self.save(update_fields=["status"])
    
    def get_borrower(self):
        """
        Возвращает читателя, который в данный момент держит книгу.
        
        Returns:
            Member or None: Читатель-держатель или None, если книга не выдана
        """
        if self.status == self.STATUS_BORROWED:
            try:
                return self.borrowedbook.borrower
            except AttributeError:
                return None
        return None

    def __str__(self):
        """
        Возвращает строковое представление экземпляра книги.
        
        Returns:
            str: Строка в формате "Экземпляр книги: название (штрих-код)"
        """
        return f"Экземпляр книги: {self.book.title} ({self.barcode})"

    class Meta:
        verbose_name = "Экземпляр книги"
        verbose_name_plural = "Экземпляры книг"
        # Сортировка по штрих-коду
        ordering = ['barcode']
        # Индексы для быстрого поиска
        indexes = [
            models.Index(fields=['barcode']),
            models.Index(fields=['status']),
            models.Index(fields=['publication_date']),
        ]


User = get_user_model()


class Borrowing(models.Model):
    """
    УСТАРЕВШАЯ модель выдачи книги.
    
    ВНИМАНИЕ: Эта модель больше не используется в системе!
    Вместо неё используется модель BorrowedBook из приложения borrowing.
    
    Оставлена для совместимости со старыми данными.
    Рекомендуется к удалению после миграции всех данных.
    
    Attributes:
        user (ForeignKey): Пользователь, взявший книгу
        book (ForeignKey): Экземпляр выданной книги  
        borrow_date (DateTimeField): Дата и время выдачи
        return_date (DateTimeField): Дата и время возврата
    """
    # УСТАРЕВШИЕ ПОЛЯ - НЕ ИСПОЛЬЗОВАТЬ!
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        help_text="УСТАРЕЛО: Используйте BorrowedBook.borrower"
    )
    book = models.ForeignKey(
        BookItem,
        on_delete=models.CASCADE,
        verbose_name="Экземпляр книги",
        help_text="УСТАРЕЛО: Используйте BorrowedBook.book_item"
    )
    borrow_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата выдачи",
        help_text="УСТАРЕЛО: Используйте BorrowedBook.borrowed_date"
    )
    return_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата возврата",
        help_text="УСТАРЕЛО: Логика возврата изменена в BorrowedBook"
    )

    def __str__(self):
        """
        Возвращает строковое представление устаревшей выдачи.
        
        Returns:
            str: Строка с предупреждением об устаревшей модели
        """
        return f"[УСТАРЕЛО] Выдача: {self.book.book.title} → {self.user.username}"

    class Meta:
        verbose_name = "Выдача книги (устарело)"
        verbose_name_plural = "Выдачи книг (устарело)"
        # Помечаем как устаревшую
        db_table = 'library_borrowing_deprecated'
