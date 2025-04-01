FROM python:3.10-slim

WORKDIR /app

# Установка зависимостей для сборки пакетов
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копирование зависимостей
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Команда для запуска приложения
CMD ["python", "main.py", "--start"]