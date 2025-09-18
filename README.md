# 📚 DRF Library - REST API для управления библиотекой

## 📖 Описание проекта

Этот проект представляет собой полнофункциональный REST API, разработанный на фреймворке Django с использованием Django Rest Framework (DRF). API предназначен для управления цифровой библиотекой, предоставляя функционал для управления книгами, авторами, экземплярами книг и записями о выдаче книг.

## ✨ Ключевые возможности

### 🔐 Авторизация и аутентификация
- **JWT токены** для защиты API-маршрутов
- **Регистрация пользователей** с подтверждением пароля
- **Система ролей**: Администратор, Библиотекарь, Участник
- **Автоматическое обновление токенов**

### 📚 Управление контентом
- **Полный CRUD** для книг, авторов и экземпляров книг
- **Вложенные маршруты** для экземпляров книг (`/books/{id}/items/`)
- **Фильтрация и поиск** по названию, автору, ISBN
- **Статусы экземпляров**: Доступна, Выдана, Зарезервирована, Утеряна

### 📋 Система выдачи книг
- **Отслеживание выдачи** с датами возврата
- **Контроль доступа** (только библиотекари и админы могут создавать/удалять выдачи)
- **Автоматическое управление статусами** экземпляров

### 📊 Дополнительные возможности
- **Автоматическая документация API** (Swagger/OpenAPI)
- **Соответствие стандартам PEP8**
- **Docker контейнеризация**
- **HTML отчеты о покрытии кода**

## 🏗️ Архитектура проекта

```
DRF_Library/
├── accounts/          # Управление пользователями и ролями
├── library/           # Книги, авторы, экземпляры
├── borrowing/         # Система выдачи книг
├── core/              # Базовые модели
└── config/            # Настройки Django
```

## 🛠️ Технические требования

- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Python** 3.12
- **PostgreSQL** 13+

## 📦 Установленные зависимости

- **Django** 5.2.6
- **Django REST Framework** 3.16.1
- **JWT Authentication** (djangorestframework-simplejwt)
- **API Documentation** (drf-spectacular)
- **Filtering** (django-filter)
- **CORS** (django-cors-headers)
- **Environment** (django-environ)
- **Testing** (coverage, flake8)

## 🚀 Инструкции по установке и запуску

### 1. Клонирование репозитория
```bash
git clone https://github.com/Doczadrot/DRF_Library.git
cd DRF_Library
```

### 2. Настройка переменных окружения
Создайте файл `.env` в корневой директории проекта, используя `.env_sample` в качестве примера:

```bash
cp .env_sample .env
```

Отредактируйте `.env` файл:
```env
DEBUG=True
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=localhost,127.0.0.1,testserver

# PostgreSQL настройки
POSTGRES_DB=your_database_name
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_secure_password
DB_HOST=db
DB_PORT=5432
```

### 3. Запуск проекта
```bash
# Сборка и запуск контейнеров
docker-compose up --build

# Или в фоновом режиме
docker-compose up -d --build
```

### 4. Создание суперпользователя
```bash
docker-compose run --rm web python manage.py createsuperuser
```

### 5. Применение миграций
```bash
docker-compose run --rm web python manage.py migrate
```

## 🌐 Доступные эндпоинты

### 🔐 Аутентификация
- `POST /api/auth/registration/` - Регистрация пользователя
- `POST /api/token/` - Получение JWT токена
- `POST /api/token/refresh/` - Обновление токена

### 📚 Библиотека
- `GET /library/api/authors/` - Список авторов
- `GET /library/api/books/` - Список книг
- `GET /library/api/books/{id}/items/` - Экземпляры книги

### 👥 Пользователи
- `GET /accounts/api/accounts/members/` - Участники (только для библиотекарей)
- `GET /accounts/api/accounts/librarians/` - Библиотекари (только для админов)

### 📋 Выдача книг
- `GET /api/books/` - Список выдач (только для авторизованных)
- `POST /api/books/` - Создание выдачи (только для библиотекарей)

### 📖 Документация
- `GET /api/docs/` - Swagger UI документация
- `GET /api/schema/` - OpenAPI схема

## 🧪 Тестирование

### Запуск тестов
```bash
docker-compose run --rm web python manage.py test
```

### Покрытие кода
```bash
# Генерация отчета о покрытии
docker-compose run --rm web python -m coverage run --source='.' manage.py test
docker-compose run --rm web python -m coverage html

# Отчет будет доступен в папке htmlcov/index.html
```

### Проверка стиля кода
```bash
docker-compose run --rm web flake8 .
```

## 📊 Статистика проекта

- **Количество тестов**: 13
- **Соответствие PEP8**: ✅
- **Количество эндпоинтов**: 15+
- **Поддерживаемые форматы**: JSON

## 🔧 Управление проектом

### Просмотр логов
```bash
docker-compose logs -f web
```

### Остановка проекта
```bash
docker-compose down
```

### Пересборка контейнеров
```bash
docker-compose down
docker-compose up --build
```

## 📝 Примеры использования

### Регистрация пользователя
```bash
curl -X POST http://localhost:8000/api/auth/registration/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "strong_password123",
    "password2": "strong_password123"
  }'
```

### Получение токена
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "strong_password123"
  }'
```

### Создание автора
```bash
curl -X POST http://localhost:8000/library/api/authors/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Лев Толстой",
    "description": "Русский писатель"
  }'
```

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/AmazingFeature`)
3. Зафиксируйте изменения (`git commit -m 'Add some AmazingFeature'`)
4. Отправьте в ветку (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для получения дополнительной информации.

## 👨‍💻 Автор

**Иван** - (https://github.com/Doczadrot)

## 📞 Поддержка

Если у вас есть вопросы или предложения, пожалуйста, создайте issue в репозитории.

---

**Спасибо за использование DRF Library! 📚✨***
