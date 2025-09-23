from rest_framework import serializers

from ..models import Book, BookItem, Author


class AuthorSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения информации об авторе.
    
    Базовый сериализатор, предоставляющий основную информацию
    об авторе без дополнительных связанных данных.
    
    Fields:
        id (int): Уникальный идентификатор автора
        name (str): Полное имя автора
        description (str): Биография или описание автора
        
    Usage:
        Используется в качестве вложенного сериализатора
        в BookSerializer и для базовых операций CRUD с авторами.
    """
    class Meta:
        model = Author
        fields = ("id", "name", "description")
        read_only_fields = ("id",)


class AuthorListSerializer(serializers.ModelSerializer):
    """
    Расширенный сериализатор автора для списочных представлений.
    
    Включает дополнительную информацию о книгах автора,
    что полезно для отображения полной информации в списках.
    
    Fields:
        id (int): Уникальный идентификатор автора
        name (str): Полное имя автора  
        description (str): Биография или описание автора
        books (QuerySet): Список книг данного автора
        
    Note:
        Используется только для операций чтения списков авторов.
        Для создания/обновления используйте AuthorSerializer.
    """
    class Meta:
        model = Author
        fields = ("id", "name", "description", "books")
        read_only_fields = ("id", "books")


class BookSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения полной информации о книге.
    
    Предоставляет детальную информацию о книге, включая
    вложенную информацию об авторах. Используется для
    чтения данных в API.
    
    Fields:
        id (int): Уникальный идентификатор книги
        title (str): Название книги
        isbn (str): Международный стандартный номер книги
        author (List[AuthorSerializer]): Список авторов книги
        subject (str): Тематическая категория
        page_counts (int): Количество страниц
        
    Note:
        Для создания/обновления книг используйте BookCreateUpdateSerializer.
    """
    # Вложенный сериализатор для отображения авторов
    author = AuthorSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = ("id", "title", "isbn", "author", "subject", "page_counts")
        read_only_fields = ("id",)


class BookCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления книг.
    
    Упрощенная версия сериализатора без вложенных данных,
    оптимизированная для операций записи. Авторы указываются
    по их ID, а не как вложенные объекты.
    
    Fields:
        title (str): Название книги
        isbn (str): ISBN номер (должен быть уникальным)
        author (List[int]): Список ID авторов
        subject (str): Тематическая категория
        page_counts (int): Количество страниц
        
    Validation:
        - ISBN должен быть уникальным
        - Все указанные авторы должны существовать
        - page_counts должно быть положительным числом
    """
    class Meta:
        model = Book
        fields = ("title", "isbn", "author", "subject", "page_counts")
        extra_kwargs = {
            'isbn': {'required': True},
            'title': {'required': True},
            'author': {'required': True}
        }


class BookItemSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения информации об экземпляре книги.
    
    Предоставляет полную информацию об экземпляре книги,
    включая детали самой книги. Используется для чтения данных.
    
    Fields:
        id (int): Уникальный идентификатор экземпляра
        book (BookSerializer): Вложенная информация о книге
        barcode (str): Штрих-код экземпляра
        status (str): Текущий статус экземпляра
        publication_date (date): Дата публикации издания
        
    Note:
        Включает полную информацию о книге и её авторах.
        Для создания/обновления используйте BookItemCreateUpdateSerializer.
    """
    # Вложенный сериализатор для отображения информации о книге
    book = BookSerializer(read_only=True)

    class Meta:
        model = BookItem
        fields = ("id", "book", "barcode", "status", "publication_date")
        read_only_fields = ("id", "book")


class BookItemCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления экземпляров книг.
    
    Упрощенная версия для операций записи. Книга определяется
    автоматически из контекста URL (вложенный маршрут).
    
    Fields:
        id (int): Уникальный идентификатор (только для обновления)
        barcode (str): Уникальный штрих-код экземпляра
        status (str): Статус экземпляра (A/B/R/L)
        publication_date (date): Дата публикации издания
        
    Context Requirements:
        - book_id: ID книги, к которой относится экземпляр
        
    Validation:
        - barcode должен быть уникальным
        - status должен быть одним из допустимых значений
        - publication_date не может быть в будущем
    """
    class Meta:
        model = BookItem
        fields = ("id", "barcode", "status", "publication_date")
        extra_kwargs = {
            'barcode': {'required': True},
            'status': {'required': True},
            'publication_date': {'required': True}
        }

    def create(self, validated_data):
        """
        Создание нового экземпляра книги.
        
        Автоматически связывает экземпляр с книгой,
        указанной в контексте URL.
        
        Args:
            validated_data (dict): Валидированные данные экземпляра
            
        Returns:
            BookItem: Созданный экземпляр книги
            
        Raises:
            KeyError: Если book_id отсутствует в контексте
        """
        # Получаем ID книги из контекста (из URL)
        book_id = self.context["book_id"]
        # Создаем экземпляр книги, связанный с указанной книгой
        return BookItem.objects.create(book_id=book_id, **validated_data)
