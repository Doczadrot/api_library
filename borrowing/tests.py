from datetime import date, timedelta

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import User
from accounts.models import Member, Librarian
from library.models import Author, Book, BookItem
from .models import BorrowedBook


def get_jwt_for_user(user: User) -> str:
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


class BorrowingApiTests(APITestCase):
    def setUp(self):
        # Users
        self.admin = User.objects.create_user(username="admin", email="admin@example.com", password="Admin_pass_123!")
        self.admin.is_staff = True
        self.admin.save(update_fields=["is_staff"])

        self.librarian_user = User.objects.create_user(username="lib", email="lib@example.com", password="Lib_pass_123!")
        self.member_user = User.objects.create_user(username="mem", email="mem@example.com", password="Mem_pass_123!")

        # Roles
        Librarian.objects.create(user=self.librarian_user, staff_code="LIB0001")
        self.member = Member.objects.create(user=self.member_user, membership_code="MEM0001")

        # Book and item
        self.author = Author.objects.create(name="Author One")
        self.book = Book.objects.create(title="Book One", isbn="ISBN-0001", subject="Test", page_counts=100)
        self.book.author.add(self.author)
        self.book_item = BookItem.objects.create(
            book=self.book,
            barcode="BAR0001",
            status=BookItem.STATUS_AVAILABLE,
            publication_date=date(2020, 1, 1),
        )

        self.list_url = "/api/books/"  # BorrowedBookViewset router

    def auth_client(self, user: User) -> APIClient:
        client = APIClient()
        token = get_jwt_for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return client

    def test_requires_auth_for_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, msg="Должен быть 401 без авторизации")

    def test_admin_can_create_borrowed_book(self):
        client = self.auth_client(self.admin)
        payload = {
            "book_item": self.book_item.id,
            "borrower": self.member.id,
            "due_date": (date.today() + timedelta(days=7)).isoformat(),
        }
        response = client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg="Админ должен уметь создавать выдачу")
        self.assertEqual(BorrowedBook.objects.count(), 1, msg="Должна быть создана одна запись выдачи")

    def test_member_cannot_create_borrowed_book(self):
        client = self.auth_client(self.member_user)
        payload = {
            "book_item": self.book_item.id,
            "borrower": self.member.id,
            "due_date": (date.today() + timedelta(days=3)).isoformat(),
        }
        response = client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, msg="Обычный участник не должен создавать выдачу")
        self.assertEqual(BorrowedBook.objects.count(), 0, msg="Запись не должна создаваться")

    def test_librarian_can_delete_borrowed_book(self):
        # Pre-create borrowing
        borrowing = BorrowedBook.objects.create(
            book_item=self.book_item,
            borrower=self.member,
            due_date=date.today() + timedelta(days=5),
        )
        client = self.auth_client(self.librarian_user)
        url = f"/api/books/{borrowing.id}/"
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, msg="Библиотекарь должен уметь удалять выдачу")
        self.assertEqual(BorrowedBook.objects.count(), 0, msg="Запись должна быть удалена")

# Create your tests here.
