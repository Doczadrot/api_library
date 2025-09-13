from django.db import models
from django.contrib.auth import get_user_model


class Author(models.Model):
    name = models.CharField(max_length=255, verbose_name="Имя")
    description = models.TextField(null=True, blank=True, verbose_name="Описание")

    def __str__(self):
        return f"Автор: {self.name}"

    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"


# Модель книги
class Book(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    isbn = models.CharField(max_length=100, unique=True, verbose_name="ISBN")
    author = models.ManyToManyField(Author, related_name="books", verbose_name="Автор")
    subject = models.CharField(max_length=127, verbose_name="Тема")
    page_counts = models.IntegerField(null=True, blank=True, verbose_name="Количество страниц")

    def __str__(self):
        return f"Книга: {self.title}"

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"


# Модель состояния книги
class BookItem(models.Model):
    STATUS_AVAILABLE = "A"
    STATUS_BORROWED = "B"
    STATUS_RESERVED = "R"
    STATUS_LOST = "L"

    STATUS_CHOICES = (
        (STATUS_AVAILABLE, "Доступна"),
        (STATUS_BORROWED, "Выдана"),
        (STATUS_RESERVED, "Зарезервирована"),
        (STATUS_LOST, "Утеряна"),
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="book_items", verbose_name="Книга")
    barcode = models.CharField(max_length=15, unique=True, verbose_name="Штрих-код")
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, verbose_name="Статус")
    publication_date = models.DateField(verbose_name="Дата публикации")

    def is_available(self):
        return self.status == self.STATUS_AVAILABLE

    def change_status(self, to: str):
        self.status = to
        self.save(update_fields=["status"])

    def __str__(self):
        return f"Экземпляр книги: {self.book.title}"

    class Meta:
        verbose_name = "Экземпляр книги"
        verbose_name_plural = "Экземпляры книг"


User = get_user_model()


# Модель выдачи книги
class Borrowing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    book = models.ForeignKey(BookItem, on_delete=models.CASCADE, verbose_name="Экземпляр книги")
    borrow_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата выдачи")
    return_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата возврата")

    def __str__(self):
        return f"Выдача книги: {self.book.book.title} пользователю {self.user.username}"

    class Meta:
        verbose_name = "Выдача книги"
        verbose_name_plural = "Выдачи книг"
