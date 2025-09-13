from django.contrib import admin
from .models import Librarian, Member

# Регистрируем модели Librarian и Member
admin.site.register(Librarian)
admin.site.register(Member)

