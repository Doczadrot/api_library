from django.db import models
from django.conf import settings


# Модель библиотекаря
class Librarian(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    staff_code = models.CharField(max_length=8, verbose_name="Код сотрудника")

    def __str__(self):
        return f"Библиотекарь: {self.user.username}"


# Модель участника
class Member(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    membership_code = models.CharField(max_length=8, verbose_name="Код читателя")

    def __str__(self):
        return f"Читатель: {self.user.username}"
