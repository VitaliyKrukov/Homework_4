from rest_framework import viewsets

from .models import Payment
from .serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet для платежей с простой фильтрацией"""

    serializer_class = PaymentSerializer

    def get_queryset(self):
        queryset = Payment.objects.all()

        course_id = self.request.query_params.get("course")
        if course_id:
            queryset = queryset.filter(paid_course_id=course_id)

        lesson_id = self.request.query_params.get("lesson")
        if lesson_id:
            queryset = queryset.filter(paid_lesson_id=lesson_id)

        payment_method = self.request.query_params.get("method")
        if payment_method in ["cash", "transfer"]:
            queryset = queryset.filter(payment_method=payment_method)

        ordering = self.request.query_params.get("ordering", "desc")
        if ordering == "asc":
            queryset = queryset.order_by("payment_date")
        else:
            queryset = queryset.order_by("-payment_date")

        return queryset
