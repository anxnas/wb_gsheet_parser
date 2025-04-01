import argparse

from utils import log, setup_logging
from config import settings
from services import WorkerService, BeatService, CeleryProcessManager, CheckService


def main():
    """Основная функция запуска приложения."""
    # Настраиваем логирование
    setup_logging()

    parser = argparse.ArgumentParser(description='Парсер позиций товаров в поисковой выдаче Wildberries')
    parser.add_argument('--check', action='store_true', help='Выполнить одиночную проверку позиции')
    parser.add_argument('--worker', action='store_true', help='Запустить только Celery worker')
    parser.add_argument('--beat', action='store_true', help='Запустить только Celery beat')
    parser.add_argument('--start', action='store_true', help='Запустить весь сервис (worker и beat)')
    args = parser.parse_args()

    if args.check:
        # Запускаем одиночную проверку
        CheckService.run_check()
    elif args.worker:
        # Запускаем только worker
        WorkerService.start_worker()
    elif args.beat:
        # Запускаем только beat
        BeatService.start_beat()
    elif args.start:
        # Запускаем оба компонента в отдельных процессах
        process_manager = CeleryProcessManager()
        worker_process, beat_process = process_manager.start_celery_processes()

        try:
            # Ожидаем завершения процессов
            worker_process.join()
            beat_process.join()
        except KeyboardInterrupt:
            log.info("Получен сигнал прерывания. Завершаем работу...")
            process_manager.stop_celery_processes()
    else:
        # Выводим инструкцию по запуску
        print(f"""
Парсер позиций товаров в поисковой выдаче Wildberries - {settings.APP_NAME} (v{settings.APP_VERSION})

Для запуска сервиса используйте следующие команды:
1. Запуск всего сервиса: python main.py --start
2. Запуск только Celery worker: python main.py --worker
3. Запуск только Celery beat: python main.py --beat
4. Выполнение одиночной проверки: python main.py --check
        """)


if __name__ == "__main__":
    main()