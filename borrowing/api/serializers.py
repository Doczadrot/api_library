from rest_framework import serializers
from datetime import date, timedelta

from library.api.serializers import BookItemSerializer
from accounts.api.serializers import MemberSerializer
from ..models import BorrowedBook


class BorrowedBookSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения информации о выдаче книги.
    
    Предоставляет полную информацию о выдаче книги, включая
    детали экземпляра книги и информацию о читателе.
    Используется для чтения данных.
    
    Fields:
        id (int): Уникальный идентификатор выдачи
        book_item (BookItemSerializer): Вложенная информация об экземпляре книги
        borrower (MemberSerializer): Вложенная информация о читателе
        borrowed_date (date): Дата выдачи книги
        due_date (date): Планируемая дата возврата
        
    Additional Info:
        - Автоматически отображает статус просрочки
        - Включает полную информацию о книге и авторах
        - Содержит данные о читателе
        
    Note:
        Для создания выдач используйте BorrowedBookCreateSerializer.
    """
    # Вложенный сериализатор для отображения информации об экземпляре книги
    book_item = BookItemSerializer(read_only=True)
    
    # Вложенный сериализатор для отображения информации о читателе
    borrower = MemberSerializer(read_only=True)
    
    # Дополнительные поля для удобства
    is_overdue = serializers.SerializerMethodField()
    days_overdue = serializers.SerializerMethodField()

    class Meta:
        model = BorrowedBook
        fields = (
            "id", "book_item", "borrower", "borrowed_date", 
            "due_date", "is_overdue", "days_overdue"
        )
        read_only_fields = ("id", "borrowed_date")
    
    def get_is_overdue(self, obj):
        """
        Определяет, просрочена ли выдача.
        
        Args:
            obj (BorrowedBook): Экземпляр выдачи
            
        Returns:
            bool: True, если выдача просрочена
        """
        return obj.is_overdue()
    
    def get_days_overdue(self, obj):
        """
        Возвращает количество дней просрочки.
        
        Args:
            obj (BorrowedBook): Экземпляр выдачи
            
        Returns:
            int or None: Количество дней просрочки или None
        """
        return obj.how_many_days_past_from_due_date()


class BorrowedBookCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания новой выдачи книги.
    
    Упрощенная версия для операций записи. Позволяет
    библиотекарям создавать выдачи книг читателям.
    
    Fields:
        book_item (int): ID экземпляра книги для выдачи
        borrower (int): ID читателя, получающего книгу
        due_date (date): Планируемая дата возврата
        
    Validation:
        - Экземпляр книги должен быть доступен для выдачи
        - Читатель должен существовать и быть активным
        - Дата возврата должна быть в будущем
        - Один экземпляр может быть выдан только одному читателю
        
    Automatic Fields:
        - borrowed_date: Устанавливается автоматически на текущую дату
        
    Note:
        После создания выдачи статус экземпляра книги
        автоматически изменяется на "Выдана".
    """
    class Meta:
        model = BorrowedBook
        fields = ("book_item", "borrower", "due_date")
        extra_kwargs = {
            'book_item': {'required': True},
            'borrower': {'required': True},
            'due_date': {'required': True}
        }
    
    def validate_book_item(self, value):
        """
        Валидация экземпляра книги.
        
        Args:
            value (BookItem): Экземпляр книги для валидации
            
        Returns:
            BookItem: Валидированный экземпляр
            
        Raises:
            ValidationError: Если книга недоступна для выдачи
        """
        if not value.is_available():
            raise serializers.ValidationError(
                "Данный экземпляр книги недоступен для выдачи."
            )
        return value
    
    def validate_due_date(self, value):
        """
        Валидация даты возврата.
        
        Args:
            value (date): Дата возврата для валидации
            
        Returns:
            date: Валидированная дата
            
        Raises:
            ValidationError: Если дата некорректна
        """
        if value <= date.today():
            raise serializers.ValidationError(
                "Дата возврата должна быть в будущем."
            )
        
        # Проверяем, что дата возврата не слишком далеко в будущем (например, не более 6 месяцев)
        max_date = date.today() + timedelta(days=180)
        if value > max_date:
            raise serializers.ValidationError(
                "Дата возврата не может быть более чем через 6 месяцев."
            )
            
        return value
    
    def create(self, validated_data):
        """
        Создание новой выдачи книги.
        
        Автоматически изменяет статус экземпляра книги на "Выдана"
        и создает запись о выдаче.
        
        Args:
            validated_data (dict): Валидированные данные выдачи
            
        Returns:
            BorrowedBook: Созданная выдача
        """
        # Создаем выдачу
        borrowed_book = super().create(validated_data)
        
        # Изменяем статус экземпляра книги на "Выдана"
        book_item = borrowed_book.book_item
        book_item.change_status(book_item.STATUS_BORROWED)
        
        return borrowed_book
