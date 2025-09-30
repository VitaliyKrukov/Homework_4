from django.urls import include, path
from rest_framework.routers import SimpleRouter

from courses.apps import CoursesConfig
from courses.views import (CourseViewSet, lessonCreateAPIView,
                           lessonDestroyAPIView, lessonListAPIView,
                           lessonRetrieveAPIView, lessonUpdateAPIView)

app_name = CoursesConfig.name

router = SimpleRouter()
router.register("", CourseViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("lessons/", lessonListAPIView.as_view(), name="lesson_list"),
    path("lessons/create/", lessonCreateAPIView.as_view(), name="lesson_create"),
    path("lessons/<int:pk>/", lessonRetrieveAPIView.as_view(), name="lesson_detail"),
    path(
        "lessons/<int:pk>/update/", lessonUpdateAPIView.as_view(), name="lesson_update"
    ),
    path(
        "lessons/<int:pk>/delete/", lessonDestroyAPIView.as_view(), name="lesson_delete"
    ),
]
