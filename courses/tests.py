from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from courses.models import Course, Lesson, Subscription
from users.models import CustomUser


class LessonCRUDTestCase(APITestCase):
    def setUp(self):
        """Заполнение базы тестовыми данными"""
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com", password="testpass123"
        )
        self.moder_user = CustomUser.objects.create_user(
            email="moder@example.com", password="moderpass123"
        )
        self.moder_user.is_moderator = True  # Устанавливаем флаг модератора через поле
        self.moder_user.save()

        self.other_user = CustomUser.objects.create_user(
            email="other@example.com", password="otherpass123"
        )

        self.course = Course.objects.create(
            title="Test Course", description="Test Course Description", owner=self.user
        )

        self.lesson = Lesson.objects.create(
            title="Test Lesson",
            description="Test Lesson Description",
            course=self.course,
            video_url="https://www.youtube.com/watch?v=test123",
            owner=self.user,
        )

    def test_create_lesson_authenticated_owner(self):
        """Тест создания урока аутентифицированным владельцем"""
        self.client.force_authenticate(user=self.user)

        data = {
            "title": "New Lesson",
            "description": "New Lesson Description",
            "course": self.course.id,
            "video_url": "https://www.youtube.com/watch?v=new123",
        }

        response = self.client.post(reverse("courses:lesson-create"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_create_lesson_with_invalid_url(self):
        """Тест создания урока с невалидной ссылкой"""
        self.client.force_authenticate(user=self.user)

        data = {
            "title": "New Lesson",
            "description": "New Lesson Description",
            "course": self.course.id,
            "video_url": "https://vimeo.com/test123",  # Запрещенный домен
        }

        response = self.client.post(reverse("courses:lesson-create"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("video_url", response.data)

    def test_moderator_cannot_create_lesson(self):
        """Тест что модератор не может создавать уроки"""
        self.client.force_authenticate(user=self.moder_user)

        data = {
            "title": "New Lesson",
            "description": "New Lesson Description",
            "course": self.course.id,
            "video_url": "https://www.youtube.com/watch?v=new123",
        }

        response = self.client.post(reverse("courses:lesson-create"), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SubscriptionTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com", password="testpass123"
        )

        self.course = Course.objects.create(
            title="Test Course", description="Test Course Description", owner=self.user
        )

    def test_subscribe_to_course(self):
        """Тест добавления подписки на курс"""
        self.client.force_authenticate(user=self.user)

        data = {"course_id": self.course.id}

        response = self.client.post(reverse("courses:subscription"), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка добавлена")
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_unsubscribe_from_course(self):
        """Тест удаления подписки с курса"""
        self.client.force_authenticate(user=self.user)

        # Сначала создаем подписку
        Subscription.objects.create(user=self.user, course=self.course)

        data = {"course_id": self.course.id}

        response = self.client.post(reverse("courses:subscription"), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка удалена")
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )


class PaginationTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com", password="testpass123"
        )

        self.course = Course.objects.create(
            title="Test Course", description="Test Course Description", owner=self.user
        )

        # Создаем 15 уроков
        for i in range(15):
            Lesson.objects.create(
                title=f"Lesson {i}",
                description=f"Description {i}",
                course=self.course,
                video_url=f"https://www.youtube.com/watch?v=test{i}",
                owner=self.user,
            )

    def test_lessons_pagination(self):
        """Тест пагинации для уроков"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("courses:lesson-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 10)
