# Парсер позиций товаров Wildberries

Скрипт для парсинга позиции товара в поисковой выдаче Wildberries по артикулу и поисковому запросу.

## Описание

Скрипт каждые N минут получает из Google Sheets артикул и поисковый запрос, выполняет поиск на Wildberries и записывает позицию товара в таблицу.

## Стек технологий

- Playwright - для автоматизации браузера
- BeautifulSoup4 - для парсинга HTML
- Celery - для периодического выполнения задач
- Redis - как брокер сообщений для Celery
- Google Sheets API - для работы с Google таблицами
- Loguru - для логирования

## Требования

- Python 3.9+
- Redis
- Google аккаунт и настроенный доступ к Google Sheets API

## Установка

1. Клонировать репозиторий:

```commandline
git clone https://github.com/anxnas/wb_gsheet_parser.git
cd wb_gsheet_parser
```

2. Создать и активировать виртуальное окружение:

```commandline
python -m venv venv
source venv/bin/activate # Для Windows: venv\Scripts\activate
```

3. Установить зависимости:

```commandline
pip install -r requirements.txt
```

4. Установить браузеры для Playwright:

```commandline
playwright install
```

5. Настроить переменные окружения:
Создать файл .env на основе example.env:

```commandline
cp example.env .env
```

## Настройка Google Sheets API

1. Создайте проект в [Google Cloud Console](https://console.cloud.google.com/)
2. Включите Google Sheets API для проекта
3. Создайте сервисный аккаунт и скачайте JSON с ключами
4. Поделитесь своей Google таблицей с email-адресом сервисного аккаунта

## Использование

1. Запустите Redis:

```commandline
redis-server
```

2. Запуск всего сервиса:

```commandline
python main.py --start
```

3. Выполнение одиночной проверки:

```commandline
python main.py --check
```

### Запуск с использованием Docker

1. Создать файл .env на основе .env.example:
```bash
cp .env.example .env
```

2. Настроить переменные окружения в файле .env

3. Запустить приложение с помощью Docker Compose:
```bash
docker-compose up -d
```

## Формат данных в Google Sheets

- A1: Артикул товара Wildberries
- B1: Поисковый запрос
- A2: "Время" (заголовок)
- B2: "Артикул" (заголовок)
- C2: "Позиция" (заголовок)
- A3+: Дата и время проверки
- B3+: Проверяемый артикул
- C3+: Найденная позиция (число или "Не найден")

## Логирование

Логи сохраняются в директории `logs/` и выводятся в консоль.

## Лицензия

Этот проект распространяется под лицензией MIT. См. файл LICENSE для получения дополнительной информации.

## Контакты

- Разработчик: anxnas (Хренов Святослав Валерьевич)
- Тг канал: https://t.me/anxnas

2025 год
