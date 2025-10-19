import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .models import Course, Subscription

logger = logging.getLogger(__name__)


@shared_task
def send_course_updates_digest():
    """
    Ежедневный дайджест обновлений курсов
    """
    try:
        from django.utils import timezone

        # Находим курсы, обновленные за последние 24 часа
        yesterday = timezone.now() - timezone.timedelta(days=1)
        updated_courses = Course.objects.filter(updated_at__gte=yesterday)

        total_notifications = 0

        for course in updated_courses:
            # Для каждого обновленного курса отправляем уведомления подписчикам
            subscriptions = Subscription.objects.filter(course=course)

            for subscription in subscriptions:
                user = subscription.user

                if user.email:
                    try:
                        send_mail(
                            subject=f"Ежедневный дайджест: обновление курса {course.title}",
                            message=f'Курс "{course.title}" был обновлен. Проверьте новые материалы!',
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[user.email],
                            fail_silently=False,
                        )
                        total_notifications += 1
                        logger.info(
                            f"Даджет отправлен пользователю {user.email} для курса {course.title}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Ошибка отправки даджеста пользователю {user.email}: {str(e)}"
                        )

        return {
            "status": "success",
            "message": f"Ежедневный дайджест отправлен. Уведомлений: {total_notifications}",
            "notifications_sent": total_notifications,
        }

    except Exception as e:
        logger.error(f"Ошибка в ежедневном дайджесте курсов: {str(e)}")
        return {"status": "error", "message": f"Ошибка: {str(e)}"}


@shared_task
def send_course_update_notification(course_id, update_message="Курс был обновлен"):
    """
    Асинхронная рассылка уведомлений об обновлении курса подписанным пользователям
    """
    try:
        course = Course.objects.get(id=course_id)
        subscriptions = Subscription.objects.filter(course=course)

        if not subscriptions.exists():
            logger.info(f"Нет подписчиков для курса {course.title}")
            return "Нет подписчиков для рассылки"

        sent_count = 0
        for subscription in subscriptions:
            user = subscription.user

            # Формируем тему и текст письма
            subject = f"🔔 Обновление курса: {course.title}"

            message = f"""
Здравствуйте, {user.first_name or 'уважаемый студент'}!

Курс "{course.title}" был обновлен.

Что нового:
{update_message}

Посмотреть обновления:
http://localhost:8000/courses/courses/{course_id}/

---
С уважением,
Команда образовательной платформы
"""

            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                sent_count += 1
                logger.info(f"Уведомление отправлено пользователю {user.email}")
            except Exception as e:
                logger.error(f"Ошибка отправки пользователю {user.email}: {str(e)}")

        result = f"Уведомления отправлены {sent_count} из {subscriptions.count()} подписчиков"
        logger.info(result)
        return result

    except Course.DoesNotExist:
        error_msg = f"Курс с ID {course_id} не найден"
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Ошибка при рассылке уведомлений: {str(e)}"
        logger.error(error_msg)
        return error_msg
