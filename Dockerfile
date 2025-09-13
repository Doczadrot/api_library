# Используем официальный образ Python 3.12
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости для PostgreSQL
RUN apt-get update && apt-get -y install libpq-dev gcc

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код проекта в рабочую директорию
COPY . .

# Открываем порт 8000
EXPOSE 8000

# Команда для запуска сервера Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]