import sys
import os
from loguru import logger
from config import settings

os.makedirs("logs", exist_ok=True)

def setup_logging() -> None:
    """Настройка логирования для приложения"""

    # Удаляем стандартный логгер
    logger.remove()

    # Настройка формата и уровня логирования
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format=settings.LOG_FORMAT,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    # Логирование в файл (опционально)
    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",
        rotation="00:00",  # Ротация логов в полночь
        retention="30 days",  # Хранение логов 30 дней
        compression="zip",  # Сжатие старых логов
        level="DEBUG",
        format=settings.LOG_FORMAT,
    )

    # Перехват стандартного логгирования
    logger.add(
        sys.stderr,
        level="ERROR",
        format=settings.LOG_FORMAT,
        backtrace=True,
        diagnose=True,
    )

    # Логирование необработанных исключений
    logger.add(
        "logs/errors_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="30 days",
        compression="zip",
        level="ERROR",
        format=settings.LOG_FORMAT,
        catch=True,  # Перехват всех необработанных исключений
    )


# Экспорт логгера для использования в других модулях
log = logger
