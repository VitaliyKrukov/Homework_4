from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """Кастомный менеджер для модели пользователя с email в качестве идентификатора"""

    def create_user(self, email, password=None, **extra_fields):
        """Создает и возвращает пользователя с email и паролем"""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создает и возвращает суперпользователя"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """Кастомная модель пользователя с авторизацией по email"""

    username = None
    email = models.EmailField(
        verbose_name="почта",
        unique=True,
        help_text="создайте почту",
    )
    phone = models.CharField(
        verbose_name="телефон",
        max_length=15,
        blank=True,
        null=True,
        help_text="укажите телефон",
    )
    city = models.CharField(
        verbose_name="город",
        max_length=100,
        blank=True,
        null=True,
        help_text="укажите город",
    )
    avatar = models.ImageField(
        verbose_name="Аватар",
        upload_to="users/avatars/",
        blank=True,
        null=True,
        help_text="Загрузите аватар",
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
