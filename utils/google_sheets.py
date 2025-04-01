from typing import Tuple, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build

from utils import log
from config import settings

# Области доступа для Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


class GoogleSheetsClient:
    """Клиент для работы с Google Sheets API."""

    def __init__(self, spreadsheet_id: str = settings.SPREADSHEET_ID):
        """
        Инициализация клиента Google Sheets.

        Args:
            spreadsheet_id: ID таблицы Google Sheets
        """
        self.spreadsheet_id = spreadsheet_id
        self.service = self._get_service()

    def _get_service(self):
        """
        Создает и авторизует сервис для работы с Google Sheets API.

        Returns:
            Авторизованный сервис Google Sheets
        """
        creds = None

        # Проверяем, используем ли мы учетные данные сервисного аккаунта
        if str(settings.CREDENTIALS_FILE).endswith('.json'):
            try:
                creds = service_account.Credentials.from_service_account_file(
                    settings.CREDENTIALS_FILE, scopes=SCOPES
                )
            except Exception as e:
                log.error(f"Ошибка при загрузке учетных данных сервисного аккаунта: {e}")
                raise

        if not creds:
            log.error("Не удалось создать учетные данные")
            raise ValueError("Не удалось создать учетные данные")

        try:
            service = build('sheets', 'v4', credentials=creds)
            return service
        except Exception as e:
            log.error(f"Ошибка при создании сервиса Google Sheets: {e}")
            raise

    def get_config_data(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Получает данные конфигурации из ячеек A1 и B1.

        Returns:
            Кортеж (артикул, поисковый запрос)
        """
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='A1:B1'
            ).execute()

            values = result.get('values', [])
            if not values:
                log.warning("Не найдены данные в ячейках A1:B1")
                return None, None

            row = values[0]
            article = row[0] if len(row) > 0 else None
            search_query = row[1] if len(row) > 1 else None

            return article, search_query
        except Exception as e:
            log.error(f"Ошибка при получении данных из Google Sheets: {e}")
            return None, None

    def add_position_data(self, timestamp: str, article: str, position: int) -> bool:
        """
        Добавляет данные о позиции товара в таблицу.

        Args:
            timestamp: Время в формате строки
            article: Артикул товара
            position: Позиция в поисковой выдаче

        Returns:
            bool: Успешно ли добавлены данные
        """
        try:
            # Получаем последнюю строку в таблице
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='A:C'
            ).execute()

            values = result.get('values', [])
            next_row = len(values) + 1

            # Если строки с заголовками нет, добавляем её
            if next_row == 1 or (len(values) == 1 and values[0][0] != 'Время'):
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range='A2:C2',
                    valueInputOption='USER_ENTERED',
                    body={
                        'values': [['Время', 'Артикул', 'Позиция']]
                    }
                ).execute()
                next_row = 3
            elif next_row == 2:
                next_row = 3

            # Добавляем новые данные
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f'A{next_row}:C{next_row}',
                valueInputOption='USER_ENTERED',
                body={
                    'values': [[timestamp, article, position]]
                }
            ).execute()

            log.info(f"Данные успешно добавлены в строку {next_row}")
            return True
        except Exception as e:
            log.error(f"Ошибка при добавлении данных в Google Sheets: {e}")
            return False