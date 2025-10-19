from django.contrib import admin

from users.models import CustomUser, Payment


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
        "is_moderator",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_moderator", "is_staff", "is_active", "city")
    search_fields = ("email", "first_name", "last_name", "phone")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "phone", "city", "avatar")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_moderator",  # Теперь поле существует в базе
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "amount",
        "payment_method",
        "payment_date",
        "paid_course",
        "paid_lesson",
    )
    list_filter = ("payment_method", "payment_date")
    search_fields = ("user__email", "paid_course__title", "paid_lesson__title")
