from django.db import transaction
from django.contrib.auth.password_validation import validate_password

from .models import Assignment, AttendanceRecord, Course, Enrollment, User


@transaction.atomic
def create_student(username, password, first_name="", last_name="", email=""):
    validate_password(password, user=User(username=username, first_name=first_name, last_name=last_name, email=email))
    return User.objects.create_user(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        email=email,
        role=User.Role.STUDENT,
    )


@transaction.atomic
def create_teacher(username, password, first_name="", last_name="", email=""):
    validate_password(password, user=User(username=username, first_name=first_name, last_name=last_name, email=email))
    return User.objects.create_user(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        email=email,
        role=User.Role.TEACHER,
    )


def list_people(role=None):
    queryset = User.objects.filter(is_active=True).order_by("last_name", "first_name", "username")
    if role:
        queryset = queryset.filter(role=role)
    return [
        {
            "id": user.pk,
            "username": user.username,
            "name": user.get_full_name() or user.username,
            "email": user.email,
            "role": user.role,
        }
        for user in queryset
    ]


@transaction.atomic
def create_course(title, code, teacher_username, description=""):
    teacher = User.objects.get(username=teacher_username, role=User.Role.TEACHER)
    course = Course(
        title=title,
        code=code,
        teacher=teacher,
        description=description,
    )
    course.full_clean()
    course.save()
    return {"id": course.pk, "title": course.title, "code": course.code}


def list_courses():
    return [
        {
            "id": course.pk,
            "title": course.title,
            "code": course.code,
            "teacher": course.teacher.get_full_name() or course.teacher.username,
            "active": course.is_active,
        }
        for course in Course.objects.select_related("teacher").order_by("title")
    ]


@transaction.atomic
def enroll_student(student_username, course_code):
    student = User.objects.get(username=student_username, role=User.Role.STUDENT)
    course = Course.objects.get(code=course_code, is_active=True)
    enrollment, created = Enrollment.objects.get_or_create(student=student, course=course)
    return {
        "id": enrollment.pk,
        "student": student.username,
        "course": course.code,
        "status": enrollment.status,
        "created": created,
    }


@transaction.atomic
def create_assignment(course_code, title, due_at, description="", points=100):
    course = Course.objects.get(code=course_code, is_active=True)
    assignment = Assignment(
        course=course,
        title=title,
        due_at=due_at,
        description=description,
        points=points,
    )
    assignment.full_clean()
    assignment.save()
    return {"id": assignment.pk, "title": assignment.title, "course": course.code}


@transaction.atomic
def record_attendance(course_code, student_username, date, status, note=""):
    if status not in AttendanceRecord.Status.values:
        raise ValueError(f"Unsupported attendance status: {status}")
    course = Course.objects.get(code=course_code)
    student = User.objects.get(username=student_username, role=User.Role.STUDENT)
    enrollment = Enrollment.objects.get(
        course=course,
        student=student,
        status=Enrollment.Status.ACTIVE,
    )
    record, created = AttendanceRecord.objects.update_or_create(
        course=course,
        student=student,
        date=date,
        defaults={"status": status, "note": note, "recorded_by": course.teacher},
    )
    return {
        "id": record.pk,
        "student": enrollment.student.username,
        "course": course.code,
        "date": record.date.isoformat(),
        "status": record.status,
        "created": created,
    }
