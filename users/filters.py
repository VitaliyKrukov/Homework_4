import django_filters

from .models import Payment


class PaymentFilter(django_filters.FilterSet):

    course = django_filters.NumberFilter(field_name="paid_course__id")

    lesson = django_filters.NumberFilter(field_name="paid_lesson__id")

    method = django_filters.ChoiceFilter(
        field_name="payment_method", choices=Payment.PAYMENT_METHODS
    )

    class Meta:
        model = Payment
        fields = ["course", "lesson", "method"]
