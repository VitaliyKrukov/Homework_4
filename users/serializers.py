from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import CustomUser, Payment


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
            "phone",
            "city",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user = CustomUser.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"
        read_only_fields = ["id", "date_joined", "last_login"]
        extra_kwargs = {"password": {"write_only": True}}


class PaymentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="paid_course.title", read_only=True)
    lesson_title = serializers.CharField(source="paid_lesson.title", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = [
            "payment_date",
            "stripe_session_id",
            "stripe_price_id",
            "payment_link",
        ]


class StripePaymentCreateSerializer(serializers.Serializer):
    course_id = serializers.IntegerField(required=False)
    lesson_id = serializers.IntegerField(required=False)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate(self, attrs):
        course_id = attrs.get("course_id")
        lesson_id = attrs.get("lesson_id")

        if not course_id and not lesson_id:
            raise serializers.ValidationError("Укажите course_id или lesson_id")
        if course_id and lesson_id:
            raise serializers.ValidationError("Укажите только course_id ИЛИ lesson_id")
        if not attrs.get("amount") or attrs["amount"] <= 0:
            raise serializers.ValidationError("Сумма оплаты должна быть больше 0")

        return attrs
