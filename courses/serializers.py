from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from courses.models import Course, Lesson


class CourseSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"


class LessonSerializer(ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"


class CourseDetailSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "preview",
            "description",
            "created_at",
            "updated_at",
            "lessons_count",
            "lessons",
        ]

    def get_lessons_count(self, obj):

        if hasattr(obj, "lessons_count_annotation"):
            return obj.lessons_count_annotation
        return obj.lessons.count()
