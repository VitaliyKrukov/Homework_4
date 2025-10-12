from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from .filters import PaymentFilter
from .models import Payment
from .serializers import PaymentSerializer, UserRegisterSerializer

User = get_user_model()


class PaymentViewSet(viewsets.ModelViewSet):

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter

    ordering_fields = ["payment_date", "amount"]
    ordering = ["-payment_date"]


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserRegisterSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()
