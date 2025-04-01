from utils import log
from tasks import app
from config import settings


class WorkerService:
    """Класс для управления Celery worker."""

    @staticmethod
    def start_worker():
        """
        Запускает Celery worker.

        Returns:
            None
        """
        log.info("Запуск Celery worker")

        # Используем метод Worker непосредственно из экземпляра приложения
        worker = app.Worker(
            loglevel=settings.LOG_LEVEL.lower(),
            traceback=True,
            concurrency=1,
            pool='solo'
        )
        worker.start()