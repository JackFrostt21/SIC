import logging
import time

from django.core.management.base import BaseCommand

from app.scheduler.scheduling import start_scheduler


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Запускает планировщик APScheduler."

    def handle(self, *args, **options):
        self.stdout.write("Starting scheduler...")
        start_scheduler()
        self.stdout.write("Scheduler started. Press Ctrl+C to exit.")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write("Scheduler stopped.")
        except Exception:
            logger.exception("Scheduler command crashed")
            raise
