import asyncio

from utils import log
from utils import GoogleSheetsClient
from tasks.celery_tasks import search_article_position


class CheckService:
    """Класс для выполнения одиночной проверки позиции товара."""

    @staticmethod
    async def run_single_check():
        """
        Выполняет одиночную проверку позиции товара.

        Returns:
            None
        """
        try:
            # Получаем данные конфигурации
            sheets_client = GoogleSheetsClient()
            article, search_query = sheets_client.get_config_data()

            if not article or not search_query:
                log.error("Не удалось получить артикул или поисковый запрос из Google Sheets")
                return

            log.info(f"Проверка позиции для артикула {article} по запросу '{search_query}'")

            # Запускаем поиск
            position, timestamp = await search_article_position(search_query, article)

            if position is not None:
                log.info(f"Товар с артикулом {article} найден на позиции {position}")
                # Записываем результат в таблицу
                sheets_client.add_position_data(timestamp, article, position)
            else:
                log.warning(f"Товар с артикулом {article} не найден в результатах поиска")
                # Записываем информацию о том, что товар не найден
                sheets_client.add_position_data(timestamp, article, "Не найден")

        except Exception as e:
            log.error(f"Ошибка при выполнении проверки: {e}")

    @classmethod
    def run_check(cls):
        """
        Запускает одиночную проверку в синхронном контексте.

        Returns:
            None
        """
        asyncio.run(cls.run_single_check())