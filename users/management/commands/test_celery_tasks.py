from django.core.management.base import BaseCommand

from courses.tasks import send_course_updates_digest
from users.tasks import deactivate_inactive_users, monitor_user_activity


class Command(BaseCommand):
    help = "Тестирование Celery задач"

    def handle(self, *args, **options):
        self.stdout.write("Тестирование Celery задач...")

        # Тестируем задачу деактивации пользователей
        self.stdout.write("1. Тестируем задачу деактивации неактивных пользователей...")
        result = deactivate_inactive_users.delay()
        self.stdout.write(f"   Задача запущена: {result.id}")

        # Тестируем мониторинг активности
        self.stdout.write("2. Тестируем мониторинг активности пользователей...")
        result2 = monitor_user_activity.delay()
        self.stdout.write(f"   Задача запущена: {result2.id}")

        # Тестируем дайджест курсов
        self.stdout.write("3. Тестируем ежедневный дайджест курсов...")
        result3 = send_course_updates_digest.delay()
        self.stdout.write(f"   Задача запущена: {result3.id}")

        self.stdout.write(
            self.style.SUCCESS(
                "Все задачи успешно запущены! Проверьте логи Celery worker."
            )
        )
