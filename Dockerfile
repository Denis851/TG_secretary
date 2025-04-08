# Базовый образ с Python и необходимыми инструментами
FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y build-essential gcc libffi-dev

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы
COPY . .

# Запускаем бота
CMD ["python", "main.py"]
