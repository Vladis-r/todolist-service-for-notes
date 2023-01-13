# Базовый образ, который тоже состоит из слоев
FROM python:3.10-slim
# значения переменных окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Задаём директорию
WORKDIR /app
# Копируем зависимости
COPY requirements.txt .
# Устанавливаем зависимости
RUN pip install -r requirements.txt
# Копируем код, кроме .dockerignore
COPY . .