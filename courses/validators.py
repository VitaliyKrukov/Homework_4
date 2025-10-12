from urllib.parse import urlparse

from rest_framework import serializers


def validate_youtube_url(value):
    """
    Валидатор для проверки, что ссылка ведет только на youtube.com
    """
    if not value:
        return value

    parsed_url = urlparse(value)
    domain = parsed_url.netloc.lower()

    # Разрешаем пустые значения
    if not domain:
        return value

    # Проверяем, что домен youtube.com или youtu.be
    allowed_domains = [
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "youtu.be",  # короткие ссылки YouTube
    ]

    is_allowed = any(
        domain.endswith(allowed_domain) for allowed_domain in allowed_domains
    )

    if not is_allowed:
        raise serializers.ValidationError(
            "Разрешены только ссылки на YouTube. " f"Ваша ссылка: {value}"
        )

    return value
