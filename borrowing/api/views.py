
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from datetime import date

from accounts.api.permissions import IsAdminOrLibrarian
from library.models import BookItem
from .serializers import BorrowedBookSerializer, BorrowedBookCreateSerializer
from ..models import BorrowedBook


class BorrowedBookViewset(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    """
    ViewSet для управления выдачами книг в библиотечной системе.
    
    Предоставляет функционал для создания, просмотра и удаления выдач книг.
    Доступен только аутентифицированным пользователям с правами библиотекаря.
    
    Features:
        - JWT аутентификация обязательна
        - Права доступа только для библиотекарей и администраторов
        - Автоматическое изменение статуса экземпляра при выдаче/возврате
        - Оптимизированные запросы с select_related и prefetch_related
        - Фильтрация по просроченным выдачам
        
    Supported Actions:
        - CREATE: Выдача книги читателю
        - RETRIEVE: Просмотр детальной информации о выдаче
        - LIST: Список всех выдач с фильтрацией
        - DESTROY: Возврат книги (удаление записи выдачи)
        
    Missing Actions:
        - UPDATE: Выдачи не редактируются, только создаются и удаляются
        - PARTIAL_UPDATE: Аналогично UPDATE
        
    Endpoints:
        - GET /api/books/ - Список всех выдач
        - POST /api/books/ - Создание новой выдачи
        - GET /api/books/{id}/ - Детали конкретной выдачи
        - DELETE /api/books/{id}/ - Возврат книги
        
    Permissions:
        - Только библиотекари могут управлять выдачами
        - Читатели не могут самостоятельно брать книги через API
        
    Note:
        При удалении выдачи (возврате книги) статус экземпляра
        автоматически изменяется на "Доступна".
    """
    # Оптимизированный queryset с предзагрузкой связанных данных
    queryset = (
        BorrowedBook.objects
        .select_related("book_item__book", "borrower__user")
        .prefetch_related("book_item__book__author")
        .all()
    )
    
    # Настройки аутентификации и прав доступа
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOrLibrarian]

    def get_serializer_class(self):
        """
        Возвращает соответствующий сериализатор в зависимости от действия.
        
        Returns:
            Serializer: BorrowedBookCreateSerializer для создания,
                       BorrowedBookSerializer для остальных операций
        """
        if self.action == "create":
            return BorrowedBookCreateSerializer
        return BorrowedBookSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Создание выдачи книги с автоматическим изменением статуса экземпляра.
        
        Args:
            serializer: Валидированный сериализатор создания выдачи
            
        Note:
            Использует транзакцию для атомарного создания выдачи
            и изменения статуса экземпляра книги.
        """
        # Создаем выдачу через сериализатор (статус книги меняется внутри)
        super().perform_create(serializer)

    @transaction.atomic 
    def perform_destroy(self, instance):
        """
        Возврат книги с автоматическим изменением статуса экземпляра.
        
        Args:
            instance (BorrowedBook): Возвращаемая выдача
            
        Note:
            При возврате статус экземпляра меняется на "Доступна"
            и запись выдачи удаляется.
        """
        # Получаем экземпляр книги до удаления записи выдачи
        book_item = instance.book_item
        
        # Удаляем запись выдачи
        super().perform_destroy(instance)
        
        # Возвращаем статус экземпляра в "Доступна"
        book_item.change_status(BookItem.STATUS_AVAILABLE)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """
        Получение списка просроченных выдач.
        
        Args:
            request: HTTP запрос
            
        Returns:
            Response: Список просроченных выдач с дополнительной информацией
        """
        # Фильтруем просроченные выдачи
        overdue_borrowings = self.get_queryset().filter(
            due_date__lt=date.today()
        )
        
        serializer = self.get_serializer(overdue_borrowings, many=True)
        return Response({
            'count': overdue_borrowings.count(),
            'results': serializer.data
        })

    @action(detail=False, methods=['get'])
    def due_soon(self, request):
        """
        Получение списка выдач, срок которых истекает в ближайшие дни.
        
        Args:
            request: HTTP запрос
            
        Returns:
            Response: Список выдач, которые нужно вернуть в ближайшие 3 дня
        """
        from datetime import timedelta
        
        # Выдачи, которые нужно вернуть в ближайшие 3 дня
        due_soon_date = date.today() + timedelta(days=3)
        due_soon_borrowings = self.get_queryset().filter(
            due_date__lte=due_soon_date,
            due_date__gte=date.today()
        )
        
        serializer = self.get_serializer(due_soon_borrowings, many=True)
        return Response({
            'count': due_soon_borrowings.count(),
            'results': serializer.data
        })

    @action(detail=True, methods=['patch'])
    def extend(self, request, pk=None):
        """
        Продление срока возврата книги.
        
        Args:
            request: HTTP запрос с количеством дней для продления
            pk: ID выдачи
            
        Returns:
            Response: Обновленная информация о выдаче
        """
        borrowing = self.get_object()
        extend_days = request.data.get('days', 7)  # По умолчанию 7 дней
        
        try:
            extend_days = int(extend_days)
            if extend_days <= 0 or extend_days > 30:
                return Response(
                    {'error': 'Количество дней должно быть от 1 до 30'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {'error': 'Неверный формат количества дней'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Продлеваем срок возврата
        borrowing.extend_due_date(extend_days)
        
        serializer = self.get_serializer(borrowing)
        return Response(serializer.data)
