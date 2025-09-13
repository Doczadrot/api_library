
from rest_framework.permissions import IsAuthenticated

from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins

from accounts.api.permissions import IsAdminOrLibrarian

from .serializers import BorrowedBookSerializer, BorrowedBookCreateSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..models import BorrowedBook


class BorrowedBookViewset(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = BorrowedBook.objects.select_related("book_item").all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOrLibrarian]

    def get_serializer_class(self):
        if self.action in ("create"):
            return BorrowedBookCreateSerializer
        return BorrowedBookSerializer
