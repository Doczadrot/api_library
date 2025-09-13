from datetime import date

from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from core.models import User
from .models import Author, Book, BookItem


class LibraryApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="usr", email="usr@example.com", password="User_pass_123!")
        self.admin = User.objects.create_user(username="admin", email="admin@example.com", password="Admin_pass_123!")
        self.admin.is_staff = True
        self.admin.save(update_fields=["is_staff"])
        self.client = APIClient()

        self.author1 = Author.objects.create(name="Пушкин")
        self.author2 = Author.objects.create(name="Лермонтов")

        self.book1 = Book.objects.create(title="Книга А", isbn="A-001", subject="Поэзия", page_counts=120)
        self.book1.author.add(self.author1)
        self.book2 = Book.objects.create(title="Книга Б", isbn="B-002", subject="Роман", page_counts=300)
        self.book2.author.add(self.author2)

        self.item1 = BookItem.objects.create(book=self.book1, barcode="BC-1", status=BookItem.STATUS_AVAILABLE, publication_date=date(2010, 1, 1))
        self.item2 = BookItem.objects.create(book=self.book2, barcode="BC-2", status=BookItem.STATUS_AVAILABLE, publication_date=date(2015, 6, 1))

    def test_list_books(self):
        url = "/library/books/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK, msg="Список книг должен возвращать 200")
        self.assertGreaterEqual(len(resp.data), 2, msg="В списке должно быть минимум 2 книги")

    def test_filter_books_by_title(self):
        url = "/library/books/?title=Книга А"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK, msg="Фильтрация по title должна возвращать 200")
        self.assertEqual(len(resp.data), 1, msg="Фильтр по названию должен вернуть одну книгу")
        self.assertEqual(resp.data[0]["title"], "Книга А")

    def test_list_authors(self):
        url = "/library/authors/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK, msg="Список авторов должен возвращать 200")
        self.assertGreaterEqual(len(resp.data), 2, msg="В списке авторов минимум 2 записи")

    def test_nested_book_items(self):
        url = f"/library/books/{self.book1.id}/items/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK, msg="Вложенный список экземпляров должен возвращать 200")
        self.assertEqual(len(resp.data), 1, msg="Должен быть один экземпляр для Книга А")

    def test_admin_can_create_book(self):
        self.client.force_authenticate(user=self.admin)
        payload = {
            "title": "Новая книга",
            "isbn": "NEW-123",
            "author": [self.author1.id],
            "subject": "Поэзия",
            "page_counts": 200,
        }
        url = "/library/books/"
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, msg="Админ должен уметь создавать книгу")

    def test_admin_can_update_book(self):
        self.client.force_authenticate(user=self.admin)
        payload = {
            "title": "Книга А (обновл.)",
            "isbn": self.book1.isbn,
            "author": [self.author1.id],
            "subject": "Поэзия",
            "page_counts": 150,
        }
        url = f"/library/books/{self.book1.id}/"
        resp = self.client.put(url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK, msg="Админ должен уметь обновлять книгу")

# Create your tests here.
