from django.core.management.base import BaseCommand

from courses.models import Course, Lesson
from users.models import CustomUser, Payment


class Command(BaseCommand):
    help = "Создание тестовых платежей"

    def handle(self, *args, **options):
        users = CustomUser.objects.all()
        courses = Course.objects.all()
        lessons = Lesson.objects.all()

        if not users.exists() or not courses.exists() or not lessons.exists():
            self.stdout.write(
                self.style.ERROR(
                    "Необходимо сначала создать пользователей, курсы и уроки"
                )
            )
            return

        # Данные для платежей
        payments_data = [
            {
                "user": users[0],
                "paid_course": courses[0],
                "paid_lesson": None,
                "amount": 15000.00,
                "payment_method": Payment.TRANSFER,
            },
            {
                "user": users[0],
                "paid_course": None,
                "paid_lesson": lessons[0],
                "amount": 2000.00,
                "payment_method": Payment.CASH,
            },
            {
                "user": users[1],
                "paid_course": courses[1],
                "paid_lesson": None,
                "amount": 12000.00,
                "payment_method": Payment.TRANSFER,
            },
            {
                "user": users[2],
                "paid_course": None,
                "paid_lesson": lessons[1],
                "amount": 2500.00,
                "payment_method": Payment.CASH,
            },
        ]

        created_count = 0
        for payment_data in payments_data:
            payment, created = Payment.objects.get_or_create(
                user=payment_data["user"],
                paid_course=payment_data["paid_course"],
                paid_lesson=payment_data["paid_lesson"],
                defaults={
                    "amount": payment_data["amount"],
                    "payment_method": payment_data["payment_method"],
                },
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Создан платеж: {payment}"))

        self.stdout.write(
            self.style.SUCCESS(f"Успешно создано {created_count} платежей")
        )
