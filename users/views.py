from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course, Lesson
from users.services.users.services.stripe_service import StripeService

from .filters import PaymentFilter
from .models import Payment
from .serializers import (PaymentSerializer, StripePaymentCreateSerializer,
                          UserRegisterSerializer)

User = get_user_model()


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ["payment_date", "amount"]
    ordering = ["-payment_date"]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    def create_stripe_payment(self, request):
        serializer = StripePaymentCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = request.user
                course_id = serializer.validated_data.get("course_id")
                lesson_id = serializer.validated_data.get("lesson_id")
                amount = serializer.validated_data["amount"]

                if course_id:
                    product = Course.objects.get(id=course_id)
                    product_name = product.title
                else:
                    product = Lesson.objects.get(id=lesson_id)
                    product_name = product.title

                stripe_product_id = StripeService.create_product(name=product_name)
                amount_in_cents = int(amount * 100)
                price_id = StripeService.create_price(
                    stripe_product_id, amount_in_cents
                )

                success_url = request.build_absolute_uri("/api/users/payment/success/")
                cancel_url = request.build_absolute_uri("/api/users/payment/cancel/")

                session_data = StripeService.create_checkout_session(
                    price_id, success_url, cancel_url
                )

                payment = Payment.objects.create(
                    user=user,
                    paid_course=product if course_id else None,
                    paid_lesson=product if lesson_id else None,
                    amount=amount,
                    payment_method=Payment.STRIPE,
                    stripe_session_id=session_data["session_id"],
                    stripe_price_id=price_id,
                    payment_link=session_data["payment_link"],
                    stripe_payment_status="pending",
                )

                return Response(
                    {
                        "payment_id": payment.id,
                        "payment_link": session_data["payment_link"],
                        "session_id": session_data["session_id"],
                        "amount": str(amount),
                    }
                )

            except (Course.DoesNotExist, Lesson.DoesNotExist):
                return Response({"error": "Курс или урок не найден"}, status=400)
            except Exception as e:
                return Response({"error": str(e)}, status=400)

        return Response(serializer.errors, status=400)

    @action(detail=True, methods=["get"])
    def stripe_status(self, request, pk=None):
        payment = self.get_object()

        if payment.payment_method != Payment.STRIPE:
            return Response({"error": "Это не Stripe платеж"}, status=400)

        try:
            stripe_status = StripeService.get_session_status(payment.stripe_session_id)
            payment.stripe_payment_status = stripe_status
            payment.save()

            return Response(
                {
                    "payment_id": payment.id,
                    "stripe_status": stripe_status,
                    "system_status": payment.stripe_payment_status,
                }
            )
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserRegisterSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()


class PaymentStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        session_id = request.GET.get("session_id")
        if not session_id:
            return Response({"error": "session_id обязателен"}, status=400)

        try:
            payment = Payment.objects.get(
                stripe_session_id=session_id, user=request.user
            )
            stripe_status = StripeService.get_session_status(session_id)

            payment.stripe_payment_status = stripe_status
            payment.save()

            return Response(
                {
                    "payment_id": payment.id,
                    "stripe_status": stripe_status,
                    "system_status": payment.stripe_payment_status,
                    "course": (
                        payment.paid_course.title if payment.paid_course else None
                    ),
                    "lesson": (
                        payment.paid_lesson.title if payment.paid_lesson else None
                    ),
                    "amount": str(payment.amount),
                }
            )
        except Payment.DoesNotExist:
            return Response({"error": "Платеж не найден"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class PaymentSuccessAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "success", "message": "Оплата прошла успешно"})


class PaymentCancelAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "canceled", "message": "Оплата отменена"})
