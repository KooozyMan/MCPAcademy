from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Administrator"
        TEACHER = "teacher", "Teacher"
        STUDENT = "student", "Student"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    phone = models.CharField(max_length=30, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"


class Course(models.Model):
    title = models.CharField(max_length=160)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    teacher = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="courses_taught",
        limit_choices_to={"role": User.Role.TEACHER},
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.code}: {self.title}"


class Enrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        WITHDRAWN = "withdrawn", "Withdrawn"

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="enrollments",
        limit_choices_to={"role": User.Role.STUDENT},
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ["-enrolled_at"]
        constraints = [
            models.UniqueConstraint(fields=["student", "course"], name="unique_course_enrollment"),
        ]

    def __str__(self):
        return f"{self.student} — {self.course}"


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="assignments")
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    due_at = models.DateTimeField()
    points = models.PositiveSmallIntegerField(
        default=100,
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["due_at"]

    def __str__(self):
        return f"{self.title} ({self.course.code})"


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submissions")
    content = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now=True)
    grade = models.PositiveSmallIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)

    class Meta:
        ordering = ["-submitted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["assignment", "student"],
                name="unique_assignment_submission",
            ),
        ]

    def __str__(self):
        return f"{self.student} — {self.assignment}"


class AttendanceRecord(models.Model):
    class Status(models.TextChoices):
        PRESENT = "present", "Present"
        ABSENT = "absent", "Absent"
        LATE = "late", "Late"
        EXCUSED = "excused", "Excused"

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="attendance_records")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attendance_records")
    date = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)
    note = models.CharField(max_length=255, blank=True)
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="attendance_recorded",
    )

    class Meta:
        ordering = ["-date", "student__last_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "student", "date"],
                name="unique_daily_course_attendance",
            ),
        ]

    def __str__(self):
        return f"{self.student} — {self.course} — {self.date}: {self.status}"
