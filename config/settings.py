from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Настройки приложения."""

    # Основные настройки
    APP_NAME: str = "Wildberries Parser"
    APP_VERSION: str = "0.1.0"

    # Настройки логирования
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

    # Google Sheets
    SPREADSHEET_ID: Optional[str] = None
    CREDENTIALS_FILE: str = "credentials.json"

    # Wildberries
    WB_BASE_URL: str = "https://www.wildberries.ru"
    WB_SEARCH_URL: str = f"{WB_BASE_URL}/catalog/0/search.aspx?search="

    # Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = REDIS_URL
    CELERY_RESULT_BACKEND: str = REDIS_URL

    # Интервал обновления данных (в секундах)
    UPDATE_INTERVAL: int = 600  # 10 минут

    # Безопасный поиск
    SAFE_SEARCH: bool = False
    MAX_SAFE_SEARCH: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()