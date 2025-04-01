from celery.apps.beat import Beat

from utils import log
from tasks import app
from config import settings
from utils import WorkerUtils


class BeatService:
    """Класс для управления Celery beat."""

    @staticmethod
    def start_beat():
        """
        Запускает Celery beat.

        Returns:
            None
        """
        log.info("Запуск Celery beat")
        # Настраиваем beat до запуска
        WorkerUtils.configure_beat()

        beat = Beat(app=app, loglevel=settings.LOG_LEVEL.lower())
        beat.run()