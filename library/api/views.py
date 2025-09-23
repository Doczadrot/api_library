from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q

from ..models import Book, BookItem, Author
from .filters import AuthorFilter, BookFilter, BookItemFilter
from .serializers import (
    BookSerializer,
    BookCreateUpdateSerializer,
    AuthorSerializer,
    AuthorListSerializer,
    BookItemSerializer,
    BookItemCreateUpdateSerializer,
)


class BookViewset(ModelViewSet):
    """
    ViewSet для управления книгами в библиотечной системе.
    
    Предоставляет полный CRUD функционал для работы с книгами.
    Включает поддержку фильтрации по различным параметрам.
    
    Features:
        - Фильтрация по названию, автору, ISBN, тематике
        - Оптимизированные запросы с prefetch_related для авторов
        - Различные сериализаторы для чтения и записи
        - Публичный доступ для чтения, аутентификация для записи
        
    Endpoints:
        - GET /library/books/ - Список книг с фильтрацией
        - POST /library/books/ - Создание новой книги (требует аутентификации)
        - GET /library/books/{id}/ - Детали книги
        - PUT/PATCH /library/books/{id}/ - Обновление книги
        - DELETE /library/books/{id}/ - Удаление книги
        
    Filters:
        - title: Поиск по названию (exact, icontains)
        - subject: Поиск по тематике (exact, icontains) 
        - author__name: Поиск по имени автора (exact, icontains)
        - isbn: Точный поиск по ISBN
        
    Example:
        GET /library/books/?title__icontains=python&author__name=Лутц
    """
    # Оптимизированный queryset с предзагрузкой авторов
    queryset = Book.objects.prefetch_related("author").all()
    filterset_class = BookFilter

    def get_serializer_class(self):
        """
        Возвращает соответствующий сериализатор в зависимости от действия.
        
        Returns:
            Serializer: BookCreateUpdateSerializer для записи,
                       BookSerializer для чтения
        """
        if self.action in ("create", "update", "partial_update"):
            return BookCreateUpdateSerializer
        return BookSerializer
    
    @action(detail=True, methods=['get'])
    def available_copies(self, request, pk=None):
        """
        Получение информации о доступных экземплярах книги.
        
        Args:
            request: HTTP запрос
            pk: ID книги
            
        Returns:
            Response: Информация о количестве доступных экземпляров
        """
        book = self.get_object()
        available_count = book.get_available_copies()
        total_count = book.book_items.count()
        
        return Response({
            'book_id': book.id,
            'title': book.title,
            'available_copies': available_count,
            'total_copies': total_count,
            'availability_status': 'available' if available_count > 0 else 'unavailable'
        })

    @action(detail=False, methods=['get'])
    def popular(self, request):
        """
        Получение списка популярных книг (по количеству экземпляров).
        
        Returns:
            Response: Список популярных книг
        """
        popular_books = (
            self.get_queryset()
            .annotate(copies_count=Count('book_items'))
            .filter(copies_count__gt=0)
            .order_by('-copies_count')[:10]
        )
        
        serializer = self.get_serializer(popular_books, many=True)
        return Response(serializer.data)


class AuthorViewset(ModelViewSet):
    """
    ViewSet для управления авторами в библиотечной системе.
    
    Предоставляет полный CRUD функционал для работы с авторами.
    Включает оптимизацию запросов и фильтрацию.
    
    Features:
        - Фильтрация по имени автора
        - Оптимизированные запросы для списков (с книгами)
        - Различные сериализаторы для списка и детального просмотра
        - Публичный доступ для чтения
        
    Endpoints:
        - GET /library/authors/ - Список авторов с их книгами
        - POST /library/authors/ - Создание нового автора
        - GET /library/authors/{id}/ - Детали автора
        - PUT/PATCH /library/authors/{id}/ - Обновление автора
        - DELETE /library/authors/{id}/ - Удаление автора
        
    Filters:
        - name: Поиск по имени (icontains)
        
    Note:
        При отображении списка авторов включается информация
        о связанных книгах для полноты данных.
    """
    filterset_class = AuthorFilter

    def get_queryset(self):
        """
        Возвращает оптимизированный queryset в зависимости от действия.
        
        Returns:
            QuerySet: Оптимизированный набор авторов
        """
        if self.action == "list":
            # Для списка предзагружаем связанные книги
            return Author.objects.prefetch_related("books").all()
        return Author.objects.all()

    def get_serializer_class(self):
        """
        Возвращает соответствующий сериализатор в зависимости от действия.
        
        Returns:
            Serializer: AuthorListSerializer для списка,
                       AuthorSerializer для остальных операций
        """
        if self.action == "list":
            return AuthorListSerializer
        return AuthorSerializer
    
    @action(detail=True, methods=['get'])
    def books_count(self, request, pk=None):
        """
        Получение количества книг автора.
        
        Args:
            request: HTTP запрос
            pk: ID автора
            
        Returns:
            Response: Количество книг автора
        """
        author = self.get_object()
        books_count = author.get_books_count()
        
        return Response({
            'author_id': author.id,
            'name': author.name,
            'books_count': books_count
        })


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='book_pk',
            type={'type': 'integer'},
            location=OpenApiParameter.PATH,
            description='Уникальное значение, идентифицирующее книгу-родитель.',
        ),
        OpenApiParameter(
            name='pk',
            type={'type': 'integer'},
            location=OpenApiParameter.PATH,
            description='Уникальное значение, идентифицирующее этот экземпляр книги.',
        ),
    ]
)
class BookItemViewSet(ModelViewSet):
    """
    ViewSet для управления экземплярами книг (вложенный ресурс).
    
    Предоставляет CRUD функционал для физических экземпляров книг.
    Работает как вложенный ресурс под конкретной книгой.
    
    Features:
        - Вложенная маршрутизация (/books/{book_id}/items/)
        - Фильтрация по штрих-коду, статусу, датам публикации
        - Оптимизированные запросы с select_related и prefetch_related
        - Автоматическая привязка к родительской книге
        
    Endpoints:
        - GET /library/books/{book_id}/items/ - Экземпляры конкретной книги
        - POST /library/books/{book_id}/items/ - Создание экземпляра
        - GET /library/books/{book_id}/items/{id}/ - Детали экземпляра
        - PUT/PATCH /library/books/{book_id}/items/{id}/ - Обновление
        - DELETE /library/books/{book_id}/items/{id}/ - Удаление
        
    Filters:
        - barcode: Поиск по штрих-коду
        - status: Фильтр по статусу (A/B/R/L)
        - from_date: Экземпляры опубликованные после даты
        - to_date: Экземпляры опубликованные до даты
        
    URL Structure:
        /library/books/1/items/ - все экземпляры книги с ID=1
        /library/books/1/items/5/ - экземпляр с ID=5 книги с ID=1
        
    Note:
        book_pk из URL автоматически передается в контекст сериализатора
        для правильной привязки создаваемых экземпляров.
    """
    filterset_class = BookItemFilter

    def get_queryset(self):
        """
        Возвращает экземпляры книг для конкретной книги с оптимизацией.
        
        Returns:
            QuerySet: Оптимизированный набор экземпляров конкретной книги
        """
        return (
            BookItem.objects
            .select_related("book")  # Предзагружаем информацию о книге
            .prefetch_related("book__author")  # Предзагружаем авторов
            .filter(book=self.kwargs["book_pk"])  # Фильтруем по родительской книге
        )

    def get_serializer_class(self):
        """
        Возвращает соответствующий сериализатор в зависимости от действия.
        
        Returns:
            Serializer: BookItemCreateUpdateSerializer для записи,
                       BookItemSerializer для чтения
        """
        if self.action in ("create", "update", "partial_update"):
            return BookItemCreateUpdateSerializer
        return BookItemSerializer

    def get_serializer_context(self):
        """
        Передает book_id в контекст сериализатора для создания экземпляров.
        
        Returns:
            dict: Контекст с book_id из URL
        """
        return {"book_id": self.kwargs["book_pk"]}
    
    @action(detail=False, methods=['get'])
    def available(self, request, book_pk=None):
        """
        Получение только доступных экземпляров книги.
        
        Args:
            request: HTTP запрос
            book_pk: ID книги из URL
            
        Returns:
            Response: Список доступных экземпляров
        """
        available_items = self.get_queryset().filter(
            status=BookItem.STATUS_AVAILABLE
        )
        
        serializer = self.get_serializer(available_items, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def change_status(self, request, book_pk=None, pk=None):
        """
        Изменение статуса экземпляра книги.
        
        Args:
            request: HTTP запрос с новым статусом
            book_pk: ID книги
            pk: ID экземпляра
            
        Returns:
            Response: Обновленная информация об экземпляре
        """
        item = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(BookItem.STATUS_CHOICES):
            return Response(
                {'error': 'Недопустимый статус'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        item.change_status(new_status)
        serializer = self.get_serializer(item)
        return Response(serializer.data)
