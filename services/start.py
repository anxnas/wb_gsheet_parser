from billiard.context import Process
from celery.concurrency import asynpool

from utils import log
from config import settings
from .worker import WorkerService
from .beat import BeatService


class CeleryProcessManager:
    """Класс для управления процессами Celery."""

    def __init__(self):
        """Инициализирует менеджер процессов."""
        self.worker_process = None
        self.beat_process = None

    def start_celery_processes(self):
        """
        Запускает Celery worker и beat в отдельных процессах.

        Returns:
            tuple: Кортеж из двух процессов (worker, beat)
        """
        # Закрываем пул для избежания проблем с fork на Unix-системах
        asynpool.PROC_ALIVE_TIMEOUT = 60.0

        log.info(f"Запуск парсера {settings.APP_NAME} (v{settings.APP_VERSION})")

        # Запускаем worker в отдельном процессе
        self.worker_process = Process(target=WorkerService.start_worker)
        self.worker_process.start()

        # Запускаем beat в отдельном процессе
        self.beat_process = Process(target=BeatService.start_beat)
        self.beat_process.start()

        return self.worker_process, self.beat_process

    def stop_celery_processes(self):
        """
        Останавливает запущенные процессы Celery.

        Returns:
            None
        """
        log.info("Остановка Celery процессов")

        if self.worker_process and self.worker_process.is_alive():
            self.worker_process.terminate()
            self.worker_process.join()
            log.info("Celery worker остановлен")

        if self.beat_process and self.beat_process.is_alive():
            self.beat_process.terminate()
            self.beat_process.join()
            log.info("Celery beat остановлен")