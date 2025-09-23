from rest_framework.permissions import BasePermission
from accounts.models import Librarian


class IsAdminOrLibrarian(BasePermission):
    """
    Кастомное разрешение для доступа библиотекарей и администраторов.
    
    Предоставляет доступ к ресурсам только пользователям, которые являются:
    1. Администраторами системы (is_staff=True)
    2. Библиотекарями (имеют связанную запись в модели Librarian)
    
    Usage:
        Используется в ViewSet'ах для ограничения доступа к операциям
        управления читателями, выдачами книг и другим административным функциям.
        
    Example:
        class MemberViewset(ModelViewSet):
            permission_classes = [IsAdminOrLibrarian]
            
    Security Logic:
        - Администраторы имеют полный доступ ко всем ресурсам
        - Библиотекари могут управлять читателями и выдачами
        - Обычные пользователи получают отказ в доступе
        
    Performance:
        Выполняет дополнительный запрос к базе данных для проверки
        статуса библиотекаря, но только для не-администраторов.
    """

    def has_permission(self, request, view):
        """
        Проверяет, имеет ли пользователь разрешение на выполнение запроса.
        
        Args:
            request: HTTP запрос с информацией о пользователе
            view: View, к которому осуществляется доступ
            
        Returns:
            bool: True, если доступ разрешен; False - если запрещен
            
        Logic:
            1. Проверяет аутентификацию пользователя
            2. Если пользователь - администратор (is_staff), доступ разрешен
            3. Если пользователь связан с моделью Librarian, доступ разрешен
            4. Во всех остальных случаях доступ запрещен
        """
        # Проверяем, что пользователь аутентифицирован
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Администраторы имеют полный доступ
        if request.user.is_staff:
            return True
            
        # Проверяем, является ли пользователь библиотекарем
        try:
            # Используем exists() для оптимизации запроса
            if Librarian.objects.filter(user=request.user).exists():
                return True
        except Exception:
            # В случае ошибки базы данных запрещаем доступ
            return False
            
        # Во всех остальных случаях доступ запрещен
        return False
    
    def has_object_permission(self, request, view, obj):
        """
        Проверяет разрешение на операции с конкретным объектом.
        
        Args:
            request: HTTP запрос
            view: View, обрабатывающий запрос  
            obj: Объект, к которому запрашивается доступ
            
        Returns:
            bool: True, если доступ к объекту разрешен
            
        Note:
            Использует ту же логику, что и has_permission,
            так как библиотекари имеют доступ ко всем объектам
            в рамках своих разрешений.
        """
        # Применяем ту же логику проверки разрешений
        return self.has_permission(request, view)
