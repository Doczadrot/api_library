
from django.urls import path, include
from rest_framework import routers
from .api import views as borrowing_views

router = routers.DefaultRouter()
router.register(r'books', borrowing_views.BorrowedBookViewset, basename='borrowed-book')

urlpatterns = [

    path('', include(router.urls)),
]
