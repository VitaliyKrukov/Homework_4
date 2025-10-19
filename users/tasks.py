import logging
from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def deactivate_inactive_users():
    """
    Задача для деактивации пользователей, которые не заходили более месяца
    """
    try:
        # Вычисляем дату, до которой считаем пользователя активным
        month_ago = timezone.now() - timedelta(days=30)

        # Находим пользователей, которые не заходили более месяца и еще активны
        inactive_users = User.objects.filter(last_login__lt=month_ago, is_active=True)

        count_before = inactive_users.count()

        if count_before == 0:
            logger.info("Неактивных пользователей для блокировки не найдено")
            return {
                "status": "success",
                "message": "Неактивных пользователей для блокировки не найдено",
                "deactivated_count": 0,
            }

        # Получаем email перед деактивацией для логирования
        user_emails = list(inactive_users.values_list("email", flat=True))

        # Деактивируем пользователей
        deactivated_count = inactive_users.update(is_active=False)

        # Логируем результат
        logger.info(f"Деактивировано {deactivated_count} пользователей: {user_emails}")

        return {
            "status": "success",
            "message": f"Успешно деактивировано {deactivated_count} пользователей",
            "deactivated_count": deactivated_count,
            "deactivated_users": user_emails,
        }

    except Exception as e:
        error_msg = f"Ошибка при деактивации неактивных пользователей: {str(e)}"
        logger.error(error_msg)
        return {"status": "error", "message": error_msg, "deactivated_count": 0}


@shared_task
def monitor_user_activity():
    """
    Задача для мониторинга активности пользователей (логирование статистики)
    """
    try:
        month_ago = timezone.now() - timedelta(days=30)
        week_ago = timezone.now() - timedelta(days=7)

        # Статистика по пользователям
        total_users = User.objects.count()
        active_users_month = User.objects.filter(
            last_login__gte=month_ago, is_active=True
        ).count()
        active_users_week = User.objects.filter(
            last_login__gte=week_ago, is_active=True
        ).count()
        inactive_users_to_deactivate = User.objects.filter(
            last_login__lt=month_ago, is_active=True
        ).count()
        deactivated_users = User.objects.filter(is_active=False).count()

        stats = {
            "total_users": total_users,
            "active_month": active_users_month,
            "active_week": active_users_week,
            "inactive_to_deactivate": inactive_users_to_deactivate,
            "deactivated_users": deactivated_users,
        }

        logger.info(
            f"Статистика пользователей: "
            f"Всего: {total_users}, "
            f"Активных за месяц: {active_users_month}, "
            f"Активных за неделю: {active_users_week}, "
            f"Неактивных (к деактивации): {inactive_users_to_deactivate}, "
            f"Деактивированных: {deactivated_users}"
        )

        return {"status": "success", "stats": stats}

    except Exception as e:
        logger.error(f"Ошибка при мониторинге активности пользователей: {str(e)}")
        return {"status": "error", "message": f"Ошибка: {str(e)}"}


@shared_task
def cleanup_old_payments():
    """
    Очистка старых платежей (пример задачи)
    """
    try:
        # Здесь может быть логика очистки старых платежных записей
        logger.info("Задача очистки старых платежей выполнена")
        return {"status": "success", "message": "Очистка старых платежей завершена"}
    except Exception as e:
        logger.error(f"Ошибка при очистке платежей: {str(e)}")
        return {"status": "error", "message": f"Ошибка: {str(e)}"}
