from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.views import MemberViewset, LibrarianViewset

router = DefaultRouter()
router.register(r'members', MemberViewset, basename='member')
router.register(r'librarians', LibrarianViewset, basename='librarian')

urlpatterns = [
    path('api/accounts/', include(router.urls)),
]
