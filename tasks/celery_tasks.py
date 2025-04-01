import asyncio
from celery import Celery

from utils import log
from config import settings
from utils import GoogleSheetsClient
from parser import WildberriesParser

# Создаем экземпляр Celery
app = Celery('wb_parser')

# Настройка Celery
app.conf.broker_url = settings.CELERY_BROKER_URL
app.conf.result_backend = settings.CELERY_RESULT_BACKEND
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']
app.conf.task_track_started = True
app.conf.worker_max_tasks_per_child = 50


@app.task(name='check_position')
def check_position() -> dict:
    """
    Задача Celery для проверки позиции товара в поисковой выдаче.

    Returns:
        dict: Результат выполнения задачи
    """
    log.info("Запуск задачи проверки позиции товара")

    try:
        # Получаем данные конфигурации из Google Sheets
        sheets_client = GoogleSheetsClient()
        article, search_query = sheets_client.get_config_data()

        if not article or not search_query:
            log.error("Не удалось получить артикул или поисковый запрос из Google Sheets")
            return {
                'status': 'error',
                'message': 'Отсутствуют данные артикула или поискового запроса в таблице'
            }

        log.info(f"Полученные данные: артикул={article}, запрос='{search_query}'")

        # Запускаем асинхронную функцию поиска
        position, timestamp = asyncio.run(search_article_position(search_query, article))

        # Если позиция найдена, записываем результат в таблицу
        if position is not None:
            result = sheets_client.add_position_data(timestamp, article, position)
            if result:
                return {
                    'status': 'success',
                    'article': article,
                    'search_query': search_query,
                    'position': position,
                    'timestamp': timestamp
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Ошибка при записи данных в Google Sheets'
                }
        else:
            # Записываем информацию о том, что товар не найден
            sheets_client.add_position_data(timestamp, article, "Не найден")
            return {
                'status': 'not_found',
                'article': article,
                'search_query': search_query,
                'timestamp': timestamp
            }
    except Exception as e:
        log.error(f"Ошибка при выполнении задачи: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }


async def search_article_position(search_query: str, article: str) -> tuple:
    """
    Асинхронная функция для поиска позиции товара.

    Args:
        search_query: Поисковый запрос
        article: Артикул товара

    Returns:
        tuple: (позиция товара, временная метка)
    """
    parser = WildberriesParser()
    try:
        await parser.initialize()
        return await parser.search_article_position(search_query, article)
    finally:
        await parser.close()