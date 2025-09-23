from django_filters import rest_framework as filters

from ..models import Book, Author, BookItem


class AuthorFilter(filters.FilterSet):
    """
    Фильтр для поиска авторов в библиотечной системе.
    
    Предоставляет возможность фильтрации авторов по имени
    с поддержкой нечеткого поиска (поиск по подстроке).
    
    Filters:
        name (CharField): Поиск по имени автора (регистронезависимый, подстрока)
        
    Usage:
        GET /library/authors/?name=пушкин
        GET /library/authors/?name=александр
        
    Features:
        - Поиск по подстроке (icontains) - находит "Пушкин" по запросу "пуш"
        - Регистронезависимый поиск - "пушкин" найдет "Пушкин"
        - Поиск по частичному совпадению имени и фамилии
        
    Example Results:
        ?name=толстой → найдет "Лев Толстой", "Алексей Толстой"
        ?name=лев → найдет "Лев Толстой", "Лев Гумилев"
    """
    # Поиск по имени автора с поддержкой подстроки
    name = filters.CharFilter(
        lookup_expr="icontains",
        help_text="Поиск по имени автора (регистронезависимый, поиск по подстроке)"
    )

    class Meta:
        model = Author
        fields = ["name"]


class BookFilter(filters.FilterSet):
    """
    Комплексный фильтр для поиска книг в библиотечной системе.
    
    Предоставляет множественные варианты фильтрации книг по различным критериям
    с поддержкой точного и нечеткого поиска.
    
    Available Filters:
        title (CharField): Поиск по названию книги
            - exact: Точное совпадение названия
            - icontains: Поиск по подстроке в названии
            
        subject (CharField): Поиск по тематике/жанру
            - exact: Точное совпадение тематики
            - icontains: Поиск по подстроке в тематике
            
        author__name (CharField): Поиск по имени автора
            - exact: Точное совпадение имени автора
            - icontains: Поиск по подстроке в имени автора
            
        isbn (CharField): Поиск по ISBN номеру
            - exact: Точное совпадение ISBN (единственный вариант)
            
    Usage Examples:
        GET /library/books/?title__icontains=python
        GET /library/books/?author__name__icontains=лутц
        GET /library/books/?subject=Программирование
        GET /library/books/?isbn=978-5-94723-568-9
        GET /library/books/?title__icontains=django&subject__icontains=програм
        
    Complex Queries:
        Можно комбинировать несколько фильтров:
        ?title__icontains=django&author__name__icontains=хохлов&subject=IT
        
    Performance Notes:
        - Поиск по ISBN самый быстрый (индексированное поле)
        - icontains запросы медленнее exact запросов
        - author__name использует JOIN с таблицей авторов
    """
    
    class Meta:
        model = Book
        fields = {
            "title": ["exact", "icontains"],
            "subject": ["exact", "icontains"], 
            "author__name": ["exact", "icontains"],
            "isbn": ["exact"],
        }


class BookItemFilter(filters.FilterSet):
    """
    Фильтр для поиска экземпляров книг с поддержкой диапазонов дат.
    
    Предоставляет возможность фильтрации физических экземпляров книг
    по различным критериям, включая статус и даты публикации.
    
    Standard Filters:
        barcode (CharField): Точный поиск по штрих-коду экземпляра
        status (CharField): Фильтр по статусу экземпляра (A/B/R/L)
        
    Date Range Filters:
        from_date (DateFilter): Экземпляры опубликованные ОТ указанной даты
        to_date (DateFilter): Экземпляры опубликованные ДО указанной даты
        
    Status Values:
        - A: Доступна для выдачи
        - B: Выдана читателю
        - R: Зарезервирована
        - L: Утеряна
        
    Usage Examples:
        GET /library/books/1/items/?status=A
        GET /library/books/1/items/?barcode=1234567890123
        GET /library/books/1/items/?from_date=2020-01-01
        GET /library/books/1/items/?to_date=2023-12-31
        GET /library/books/1/items/?from_date=2020-01-01&to_date=2023-12-31
        GET /library/books/1/items/?status=A&from_date=2022-01-01
        
    Date Format:
        Даты должны быть в формате YYYY-MM-DD (ISO 8601)
        
    Common Use Cases:
        - Найти все доступные экземпляры: ?status=A
        - Найти новые издания: ?from_date=2023-01-01
        - Найти экземпляры определенного периода: ?from_date=2020-01-01&to_date=2022-12-31
        - Найти конкретный экземпляр: ?barcode=1234567890123
        
    Performance:
        - barcode поиск очень быстрый (уникальный индекс)
        - status поиск быстрый (индексированное поле)
        - Диапазоны дат используют индекс на publication_date
    """
    # Фильтр для экземпляров опубликованных от указанной даты
    from_date = filters.DateFilter(
        field_name="publication_date", 
        lookup_expr="gte",
        help_text="Экземпляры опубликованные от указанной даты (включительно). Формат: YYYY-MM-DD"
    )
    
    # Фильтр для экземпляров опубликованных до указанной даты  
    to_date = filters.DateFilter(
        field_name="publication_date", 
        lookup_expr="lte",
        help_text="Экземпляры опубликованные до указанной даты (включительно). Формат: YYYY-MM-DD"
    )

    class Meta:
        model = BookItem
        fields = ["barcode", "status", "from_date", "to_date"]
        help_texts = {
            'barcode': 'Точный поиск по штрих-коду экземпляра (13 цифр)',
            'status': 'Статус экземпляра: A=Доступна, B=Выдана, R=Зарезервирована, L=Утеряна'
        }
