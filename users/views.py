from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import Payment
from .serializers import PaymentSerializer
from .filters import PaymentFilter


class PaymentViewSet(viewsets.ModelViewSet):


    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter


    ordering_fields = ['payment_date', 'amount']
    ordering = ['-payment_date']  # Сортировка по умолчанию