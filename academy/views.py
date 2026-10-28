from django.db.models import Q
from rest_framework import generics, permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Assignment, AttendanceRecord, Course, Enrollment, Submission, User
from .permissions import IsStaffOrReadOnly
from .serializers import (
    AssignmentSerializer,
    AttendanceSerializer,
    CourseSerializer,
    EnrollmentSerializer,
    StudentRegistrationSerializer,
    SubmissionSerializer,
)


class HealthView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"status": "ok", "service": "academy"})


class StudentRegistrationView(generics.CreateAPIView):
    serializer_class = StudentRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [IsStaffOrReadOnly]
    queryset = Course.objects.select_related("teacher")

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.role == User.Role.TEACHER:
            return queryset.filter(teacher=user)
        if user.role == User.Role.STUDENT:
            return queryset.filter(
                Q(is_active=True)
                | Q(enrollments__student=user)
            ).distinct()
        return queryset


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    queryset = Enrollment.objects.select_related("student", "course", "course__teacher")

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.role == User.Role.STUDENT:
            return queryset.filter(student=user)
        if user.role == User.Role.TEACHER:
            return queryset.filter(course__teacher=user)
        return queryset

    def perform_update(self, serializer):
        if self.request.user.role == User.Role.STUDENT:
            raise PermissionDenied("Students cannot update enrollment records.")
        serializer.save()


class AssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSerializer
    queryset = Assignment.objects.select_related("course", "course__teacher")
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.role == User.Role.TEACHER:
            return queryset.filter(course__teacher=user)
        if user.role == User.Role.STUDENT:
            return queryset.filter(course__enrollments__student=user).distinct()
        return queryset

    def perform_create(self, serializer):
        if self.request.user.role == User.Role.STUDENT:
            raise PermissionDenied("Only teachers and administrators can create assignments.")
        serializer.save()


class SubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = SubmissionSerializer
    queryset = Submission.objects.select_related("assignment", "assignment__course", "student")

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.role == User.Role.STUDENT:
            return queryset.filter(student=user)
        if user.role == User.Role.TEACHER:
            return queryset.filter(assignment__course__teacher=user)
        return queryset

    def perform_create(self, serializer):
        if self.request.user.role == User.Role.STUDENT:
            serializer.save(student=self.request.user)
        else:
            raise PermissionDenied("Only students can submit coursework.")

    def perform_update(self, serializer):
        user = self.request.user
        submission = self.get_object()
        if user.role == User.Role.STUDENT and submission.student_id != user.id:
            raise PermissionDenied("You can only edit your own submission.")
        if user.role == User.Role.STUDENT:
            serializer.save(student=user, grade=submission.grade, feedback=submission.feedback)
        else:
            serializer.save()


class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    queryset = AttendanceRecord.objects.select_related("course", "student", "recorded_by")

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.role == User.Role.STUDENT:
            return queryset.filter(student=user)
        if user.role == User.Role.TEACHER:
            return queryset.filter(course__teacher=user)
        return queryset

    def perform_create(self, serializer):
        if self.request.user.role == User.Role.STUDENT:
            raise PermissionDenied("Only teachers and administrators can record attendance.")
        serializer.save(recorded_by=self.request.user)

    def perform_update(self, serializer):
        if self.request.user.role == User.Role.STUDENT:
            raise PermissionDenied("Students cannot edit attendance records.")
        serializer.save(recorded_by=self.request.user)
