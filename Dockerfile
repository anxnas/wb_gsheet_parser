FROM python:3.10-slim

WORKDIR /app

# Установка зависимостей для сборки пакетов
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    wget \
    gnupg \
    # Зависимости для браузеров Playwright
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libexpat1 \
    libxcb1 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libxcursor1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*



# Копирование зависимостей
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install

# Команда для запуска приложения
CMD ["python", "main.py", "--start"]
