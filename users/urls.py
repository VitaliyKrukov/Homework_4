from django.urls import include, path
from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .apps import UsersConfig
from .views import (PaymentCancelAPIView, PaymentStatusAPIView,
                    PaymentSuccessAPIView, PaymentViewSet, UserCreateAPIView)

router = DefaultRouter()
router.register(r"payments", PaymentViewSet, basename="payment")

app_name = UsersConfig.name

urlpatterns = [
    path("", include(router.urls)),
    path("register/", UserCreateAPIView.as_view(), name="register"),
    path(
        "login/",
        TokenObtainPairView.as_view(permission_classes=(AllowAny,)),
        name="login",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(permission_classes=(AllowAny,)),
        name="token_refresh",
    ),
    path("payment/status/", PaymentStatusAPIView.as_view(), name="payment-status"),
    path("payment/success/", PaymentSuccessAPIView.as_view(), name="payment-success"),
    path("payment/cancel/", PaymentCancelAPIView.as_view(), name="payment-cancel"),
]
