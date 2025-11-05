from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from courses.models import Course, Lesson, Subscription
from courses.paginators import CoursePaginator, LessonPaginator
from courses.serializers import (
    CourseDetailSerializer,
    CourseSerializer,
    LessonSerializer,
)
from courses.tasks import send_course_update_notification  # Импортируем задачу
from users.permissions import IsModer, IsOwner


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    pagination_class = CoursePaginator

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CourseDetailSerializer
        return CourseSerializer

    def perform_create(self, serializer):
        course = serializer.save()
        course.owner = self.request.user
        course.save()

    def perform_update(self, serializer):
        instance = serializer.save()

        # Отправляем асинхронное уведомление об обновлении курса
        update_message = (
            f"Курс '{instance.title}' был обновлен. Проверьте новые материалы!"
        )
        send_course_update_notification.delay(instance.id, update_message)

        # Логируем отправку уведомления
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"Запущена задача отправки уведомлений для курса {instance.id}")

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [IsAuthenticated, ~IsModer]
        elif self.action in ["update", "retrieve", "partial_update"]:
            self.permission_classes = [IsAuthenticated, IsModer | IsOwner]
        elif self.action == "destroy":
            self.permission_classes = [IsAuthenticated, IsOwner & ~IsModer]
        elif self.action == "list":
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.is_anonymous:
            return queryset.none()

        # Модераторы видят все курсы
        if user.groups.filter(name="moderators").exists():
            return queryset

        # Обычные пользователи видят только свои курсы
        return queryset.filter(owner=user)


# Остальной код остается без изменений...
class LessonCreateAPIView(CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [~IsModer, IsAuthenticated]

    def perform_create(self, serializer):
        lesson = serializer.save()
        lesson.owner = self.request.user
        lesson.save()


class LessonListAPIView(ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = LessonPaginator


class LessonRetrieveAPIView(RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModer | IsOwner]


class LessonUpdateAPIView(UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModer | IsOwner]


class LessonDestroyAPIView(DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwner | ~IsModer]


class SubscriptionAPIView(APIView):
    """
    APIView для управления подписками на курсы
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get("course_id")

        if not course_id:
            return Response(
                {"error": "course_id обязателен"}, status=status.HTTP_400_BAD_REQUEST
            )

        course_item = get_object_or_404(Course, id=course_id)
        subs_item = Subscription.objects.filter(user=user, course=course_item)

        # Если подписка у пользователя на этот курс есть - удаляем ее
        if subs_item.exists():
            subs_item.delete()
            message = "Подписка удалена"
        # Если подписки у пользователя на этот курс нет - создаем ее
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = "Подписка добавлена"

        # Возвращаем ответ в API
        return Response({"message": message})
