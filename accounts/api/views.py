from django.contrib.auth import get_user_model
from django.db import transaction

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from ..models import Librarian, Member
from .permissions import IsAdminOrLibrarian
from .serializers import (
    MemberSerializer,
    CreateMemberSerializer,
    LibrarianSerializer,
    CreateLibrarianSerializer,
)

User = get_user_model()


class MemberViewset(ModelViewSet):
    """
    ViewSet для управления читателями библиотеки.
    
    Предоставляет полный CRUD функционал для работы с читателями.
    Доступен только библиотекарям и администраторам.
    
    Permissions:
        - IsAdminOrLibrarian: Только библиотекари и админы могут управлять читателями
        
    Features:
        - Автоматическая генерация кода читательского билета
        - Каскадное удаление связанного пользователя
        - Оптимизированные запросы с select_related
        - Различные сериализаторы для создания и отображения
        
    Endpoints:
        - GET /api/accounts/members/ - Список читателей
        - POST /api/accounts/members/ - Создание читателя
        - GET /api/accounts/members/{id}/ - Детали читателя
        - PUT/PATCH /api/accounts/members/{id}/ - Обновление читателя
        - DELETE /api/accounts/members/{id}/ - Удаление читателя
        
    Note:
        При удалении читателя также удаляется связанный пользователь.
    """
    # Оптимизированный queryset с предзагрузкой связанных данных
    queryset = Member.objects.select_related("user").all()
    permission_classes = [IsAdminOrLibrarian]

    def get_serializer_class(self):
        """
        Возвращает соответствующий сериализатор в зависимости от действия.
        
        Returns:
            Serializer: CreateMemberSerializer для создания,
                       MemberSerializer для остальных операций
        """
        if self.action == "create":
            return CreateMemberSerializer
        return MemberSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Создание читателя в рамках транзакции.
        
        Args:
            serializer: Валидированный сериализатор
            
        Note:
            Использует транзакцию для атомарного создания
            пользователя и связанного читателя.
        """
        super().perform_create(serializer)

    @transaction.atomic
    def perform_destroy(self, instance):
        """
        Удаление читателя с каскадным удалением пользователя.
        
        Args:
            instance (Member): Удаляемый читатель
            
        Note:
            Сначала удаляется связанный пользователь,
            что автоматически удаляет читателя через CASCADE.
        """
        # Удаляем связанного пользователя (читатель удалится автоматически)
        instance.user.delete()
        
    @action(detail=True, methods=['get'])
    def borrowings(self, request, pk=None):
        """
        Получение списка выдач конкретного читателя.
        
        Args:
            request: HTTP запрос
            pk: ID читателя
            
        Returns:
            Response: Список активных выдач читателя
        """
        member = self.get_object()
        borrowings = member.borrowed_books.filter(due_date__isnull=False)
        # Здесь можно добавить сериализацию borrowings
        return Response({
            'member': member.id,
            'active_borrowings_count': borrowings.count()
        })


class LibrarianViewset(ModelViewSet):
    """
    ViewSet для управления библиотекарями.
    
    Предоставляет полный CRUD функционал для работы с библиотекарями.
    Доступен только администраторам системы.
    
    Permissions:
        - IsAdminUser: Только администраторы могут управлять библиотекарями
        
    Features:
        - Автоматическая генерация кода сотрудника
        - Каскадное удаление связанного пользователя
        - Оптимизированные запросы с select_related
        - Различные сериализаторы для создания и отображения
        
    Endpoints:
        - GET /api/accounts/librarians/ - Список библиотекарей
        - POST /api/accounts/librarians/ - Создание библиотекаря
        - GET /api/accounts/librarians/{id}/ - Детали библиотекаря
        - PUT/PATCH /api/accounts/librarians/{id}/ - Обновление библиотекаря
        - DELETE /api/accounts/librarians/{id}/ - Удаление библиотекаря
        
    Security:
        Создание и управление библиотекарями - критичная операция,
        доступная только администраторам.
    """
    # Оптимизированный queryset с предзагрузкой связанных данных
    queryset = Librarian.objects.select_related("user").all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        """
        Возвращает соответствующий сериализатор в зависимости от действия.
        
        Returns:
            Serializer: CreateLibrarianSerializer для создания,
                       LibrarianSerializer для остальных операций
        """
        if self.action == "create":
            return CreateLibrarianSerializer
        return LibrarianSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Создание библиотекаря в рамках транзакции.
        
        Args:
            serializer: Валидированный сериализатор
            
        Note:
            Использует транзакцию для атомарного создания
            пользователя и связанного библиотекаря.
        """
        super().perform_create(serializer)

    @transaction.atomic
    def perform_destroy(self, instance):
        """
        Удаление библиотекаря с каскадным удалением пользователя.
        
        Args:
            instance (Librarian): Удаляемый библиотекарь
            
        Note:
            Сначала удаляется связанный пользователь,
            что автоматически удаляет библиотекаря через CASCADE.
        """
        # Удаляем связанного пользователя (библиотекарь удалится автоматически)
        instance.user.delete()
