from config import settings

class WorkerUtils:

    @staticmethod
    def configure_beat():
        """
        Конфигурирует периодические задачи для Celery beat.

        Returns:
            None
        """
        from tasks import app
        # Настройка периодических задач
        app.conf.beat_schedule = {
            'check-position-every-10-min': {
                'task': 'check_position',
                'schedule': settings.UPDATE_INTERVAL,  # Запуск каждые 10 минут
            },
        }