# Используем официальный образ Python
FROM python:3.11-slim

# Обновляем pip и устанавливаем системные зависимости для aiohttp и других
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    libpq-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . .

# Устанавливаем зависимости
RUN pip install --upgrade pip && pip install -r requirements.txt

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1

# Команда запуска приложения
CMD ["python", "main.py"]
