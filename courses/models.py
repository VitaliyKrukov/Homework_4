from django.db import models


class Course(models.Model):
    """Модель курса"""

    title = models.CharField(
        verbose_name="Название", max_length=255, help_text="укажите название"
    )
    preview = models.ImageField(
        verbose_name="изображение",
        upload_to="courses/previews/",
        blank=True,
        null=True,
        help_text="загрузите изображение",
    )
    description = models.TextField(
        verbose_name="описание", blank=True, null=True, help_text="укажите описание"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Владелец",
        help_text="Укажите владельца",
    )

    class Meta:
        verbose_name = "курс"
        verbose_name_plural = "курсы"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Lesson(models.Model):
    """Модель урока"""

    title = models.CharField(
        verbose_name="название",
        max_length=255,
        help_text="укажите название",
    )
    description = models.TextField(
        verbose_name="описание",
        blank=True,
        null=True,
        help_text="укажите описание",
    )
    preview = models.ImageField(
        verbose_name="изображение",
        upload_to="lessons/previews/",
        blank=True,
        null=True,
        help_text="загрузите изображение",
    )
    video_url = models.URLField(
        verbose_name="ссылка на видео",
        blank=True,
        null=True,
        help_text="укажите ссылку на видео",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="курс",
        default=1,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Владелец",
        help_text="Укажите владельца",
    )

    class Meta:
        verbose_name = "урок"
        verbose_name_plural = "уроки"
        ordering = ["created_at"]

    def __str__(self):
        return self.title


class Subscription(models.Model):
    """Модель подписки на обновления курса"""

    user = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        help_text="Укажите пользователя",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Курс",
        help_text="Укажите курс",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата подписки")

    class Meta:
        verbose_name = "подписка"
        verbose_name_plural = "подписки"
        unique_together = ["user", "course"]  # Одна подписка на курс для пользователя
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.course.title}"
