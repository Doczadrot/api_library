from dj_rest_auth.registration.views import RegisterView

from .serializers import CustomRegisterSerializer


# Создаю сериализатор для прохождения тестов


class CustomRegisterView(RegisterView):
    serializer_class = CustomRegisterSerializer


