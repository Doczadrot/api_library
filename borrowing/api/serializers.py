from rest_framework import serializers

from library.api.serializers import BookItemSerializer
# Импортируем модели, с которыми будем работать
from ..models import BorrowedBook


class BorrowedBookSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели BorrowedBook.
    """
    # Вложенный сериализатор для поля book_item
    book_item = BookItemSerializer()

    class Meta:
        model = BorrowedBook
        fields = ("id", "book_item", "borrower", "borrowed_date", "due_date")


class BorrowedBookCreateSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель
        model = BorrowedBook
        fields = ("book_item", "borrower", "borrowed_date", "due_date")
