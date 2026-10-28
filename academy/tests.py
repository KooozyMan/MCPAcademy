from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Assignment, Course, Enrollment, User


class AcademyApiTests(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher1",
            password="Secure-test-pass-934!",
            role=User.Role.TEACHER,
            first_name="Terry",
        )
        self.student = User.objects.create_user(
            username="student1",
            password="Secure-test-pass-935!",
            role=User.Role.STUDENT,
            first_name="Sam",
        )
        self.other_student = User.objects.create_user(
            username="student2",
            password="Secure-test-pass-936!",
            role=User.Role.STUDENT,
        )
        self.course = Course.objects.create(
            title="Algebra",
            code="ALG-101",
            teacher=self.teacher,
        )
        self.enrollment = Enrollment.objects.create(student=self.student, course=self.course)
        self.assignment = Assignment.objects.create(
            course=self.course,
            title="Homework 1",
            due_at="2030-01-01T12:00:00Z",
        )

    def test_superuser_is_an_academy_administrator(self):
        admin = User.objects.create_superuser(
            username="academyadmin",
            password="Secure-admin-pass-937!",
        )

        self.assertEqual(admin.role, User.Role.ADMIN)

    def test_student_registration_cannot_assign_teacher_role(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newstudent",
                "password": "Another-safe-pass-874!",
                "role": User.Role.TEACHER,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        user = User.objects.get(username="newstudent")
        self.assertEqual(user.role, User.Role.STUDENT)

    def test_student_only_sees_their_own_enrollments(self):
        self.client.force_authenticate(self.student)

        response = self.client.get("/api/enrollments/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["student"], self.student.pk)

    def test_student_cannot_create_course(self):
        self.client.force_authenticate(self.student)

        response = self.client.post(
            "/api/courses/",
            {"title": "Chemistry", "code": "CHEM-101", "teacher": self.teacher.pk},
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Course.objects.filter(code="CHEM-101").exists())

    def test_student_can_submit_only_for_an_active_enrollment(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(
            "/api/submissions/",
            {"assignment": self.assignment.pk, "content": "My work"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["student"], self.student.pk)

        self.client.force_authenticate(self.other_student)
        response = self.client.post(
            "/api/submissions/",
            {"assignment": self.assignment.pk, "content": "Not enrolled"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_teacher_cannot_create_a_student_submission(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.post(
            "/api/submissions/",
            {"assignment": self.assignment.pk, "content": "Teacher-created work"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)
