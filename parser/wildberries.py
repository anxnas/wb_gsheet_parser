from typing import Optional, Tuple
import asyncio
from datetime import datetime
from urllib.parse import quote
from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup

from utils import log
from config import settings


class WildberriesParser:
    """Парсер для поиска позиции товара в выдаче Wildberries."""

    def __init__(self):
        """Инициализация парсера."""
        self.browser = None
        self.context = None
        self.page = None

    async def initialize(self) -> None:
        """Инициализирует браузер и контекст Playwright."""
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=True)
            self.context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            self.page = await self.context.new_page()
            log.info("Playwright успешно инициализирован")
        except Exception as e:
            log.error(f"Ошибка при инициализации Playwright: {e}")
            if self.browser:
                await self.browser.close()
            raise

    async def close(self) -> None:
        """Закрывает все ресурсы браузера."""
        if self.browser:
            await self.browser.close()
            log.info("Браузер закрыт")

    async def search_article_position(self, search_query: str, article: str) -> Tuple[Optional[int], str]:
        """
        Ищет позицию товара по артикулу в результатах поиска.

        Args:
            search_query: Поисковый запрос
            article: Артикул товара

        Returns:
            Кортеж (позиция товара в выдаче, временная метка)
        """
        if not self.page:
            await self.initialize()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        encoded_query = quote(search_query)
        page_num = 1
        total_items_processed = 0

        while True:
            url = f"{settings.WB_SEARCH_URL}{encoded_query}&page={page_num}"

            try:
                log.info(f"Открываем страницу поиска: {url}")
                await self.page.goto(url, wait_until="networkidle")

                # Прокручиваем страницу, чтобы загрузить больше результатов
                await self._scroll_page()

                # Проверяем, есть ли результаты поиска
                if await self._check_no_results():
                    log.warning(f"Нет результатов поиска для запроса: {search_query}")
                    return None, timestamp

                # Получаем HTML страницы и ищем артикул
                html_content = await self.page.content()
                position, items_on_page = self._find_article_position(html_content, article)

                if position:
                    position += total_items_processed
                    log.info(f"Товар с артикулом {article} найден на позиции {position}")
                    return position, timestamp
                else:
                    log.warning(f"Товар с артикулом {article} не найден на странице {page_num}. Перелистываем...")
                    total_items_processed += items_on_page
                    page_num += 1

                # Для безопасности ограничиваем количество проверяемых страниц
                if settings.SAFE_SEARCH and page_num > settings.MAX_SAFE_SEARCH:
                    log.warning(f"Достигнут предел страниц поиска ({settings.MAX_SAFE_SEARCH})")
                    break

            except PlaywrightTimeoutError:
                log.error(f"Таймаут при загрузке страницы: {url}")
                return None, timestamp
            except Exception as e:
                log.error(f"Ошибка при поиске позиции товара: {e}")
                return None, timestamp

    async def _scroll_page(self, max_scrolls: int = 20) -> None:
        """
        Прокручивает страницу для загрузки дополнительных результатов.

        Args:
            max_scrolls: Максимальное количество прокруток
        """
        for i in range(max_scrolls):
            await self.page.evaluate("window.scrollBy(0, window.innerHeight)")
            await asyncio.sleep(1)  # Ждем загрузки данных

    async def _check_no_results(self) -> bool:
        """
        Проверяет, есть ли результаты поиска на странице.

        Returns:
            bool: True, если результатов нет
        """
        # Проверка наличия сообщений об отсутствии результатов
        no_results_selectors = [
            "text=По Вашему запросу ничего не найдено",
            "text=Ничего не нашлось по запросу"
        ]

        for selector in no_results_selectors:
            no_results = await self.page.query_selector(selector)
            if no_results:
                return True

        return False

    def _find_article_position(self, html_content: str, article: str) -> Optional[int]:
        """
        Ищет позицию товара с заданным артикулом в HTML контенте.

        Args:
            html_content: HTML страницы с результатами поиска
            article: Артикул товара для поиска

        Returns:
            Позиция товара или None, если товар не найден
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Находим все карточки товаров
        product_cards = soup.select('article[class*="product-card"]')

        items_count = len(product_cards)

        for position, card in enumerate(product_cards, 1):
            card_nm_id = card.get('data-nm-id')

            if card_nm_id == article:
                return position, items_count

        # Если товар не найден - возвращаем None
        return None, items_count