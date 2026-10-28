from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Assignment, AttendanceRecord, Course, Enrollment, Submission, User


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "role"]
        read_only_fields = fields


class StudentRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["id", "username", "password", "first_name", "last_name", "email"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data, role=User.Role.STUDENT)


class CourseSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.get_full_name", read_only=True)
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Role.TEACHER),
        required=False,
    )

    class Meta:
        model = Course
        fields = [
            "id", "title", "code", "description", "teacher", "teacher_name",
            "is_active", "created_at",
        ]
        read_only_fields = ["id", "teacher_name", "created_at"]

    def validate(self, attrs):
        request = self.context.get("request")
        if request and request.user.role == User.Role.TEACHER:
            if "teacher" in attrs and attrs["teacher"] != request.user:
                raise serializers.ValidationError({"teacher": "Teachers can only manage their own courses."})
            attrs["teacher"] = request.user
        elif self.instance is None and "teacher" not in attrs:
            raise serializers.ValidationError({"teacher": "A teacher is required."})
        return attrs


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.get_full_name", read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "id", "student", "student_name", "course", "course_title",
            "enrolled_at", "status",
        ]
        read_only_fields = ["id", "student_name", "course_title", "enrolled_at"]

    def validate(self, attrs):
        request = self.context["request"]
        student = attrs.get("student", getattr(self.instance, "student", None))
        course = attrs.get("course", getattr(self.instance, "course", None))
        if request.user.role == User.Role.STUDENT:
            if self.instance:
                raise serializers.ValidationError("Students cannot edit enrollment records.")
            attrs["student"] = request.user
            if course and not course.is_active:
                raise serializers.ValidationError({"course": "This course is not open for enrollment."})
        elif student and student.role != User.Role.STUDENT:
            raise serializers.ValidationError({"student": "Enrollment requires a student account."})
        if course and request.user.role == User.Role.TEACHER and course.teacher_id != request.user.id:
            raise serializers.ValidationError({"course": "You can only manage enrollments in your courses."})
        return attrs


class AssignmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Assignment
        fields = [
            "id", "course", "course_title", "title", "description",
            "due_at", "points", "created_at",
        ]
        read_only_fields = ["id", "course_title", "created_at"]

    def validate_course(self, course):
        request = self.context["request"]
        if request.user.role == User.Role.TEACHER and course.teacher_id != request.user.id:
            raise serializers.ValidationError("You can only create assignments for your courses.")
        return course


class SubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.get_full_name", read_only=True)

    class Meta:
        model = Submission
        fields = [
            "id", "assignment", "student", "student_name", "content",
            "submitted_at", "grade", "feedback",
        ]
        read_only_fields = ["id", "student", "student_name", "submitted_at", "grade", "feedback"]

    def validate_assignment(self, assignment):
        request = self.context["request"]
        if request.user.role == User.Role.STUDENT and not Enrollment.objects.filter(
            student=request.user,
            course=assignment.course,
            status=Enrollment.Status.ACTIVE,
        ).exists():
            raise serializers.ValidationError("You must be actively enrolled in this course.")
        if request.user.role == User.Role.TEACHER and assignment.course.teacher_id != request.user.id:
            raise serializers.ValidationError("You can only manage submissions for your courses.")
        return assignment

    def create(self, validated_data):
        request = self.context["request"]
        if request.user.role == User.Role.STUDENT:
            validated_data["student"] = request.user
        return super().create(validated_data)


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.get_full_name", read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = [
            "id", "course", "course_title", "student", "student_name",
            "date", "status", "note", "recorded_by",
        ]
        read_only_fields = ["id", "course_title", "student_name", "recorded_by"]

    def validate(self, attrs):
        request = self.context["request"]
        course = attrs.get("course", getattr(self.instance, "course", None))
        student = attrs.get("student", getattr(self.instance, "student", None))
        if request.user.role == User.Role.TEACHER:
            if course and course.teacher_id != request.user.id:
                raise serializers.ValidationError({"course": "You can only record attendance for your courses."})
        if student and student.role != User.Role.STUDENT:
            raise serializers.ValidationError({"student": "Attendance requires a student account."})
        if course and student and not Enrollment.objects.filter(
            course=course,
            student=student,
            status=Enrollment.Status.ACTIVE,
        ).exists():
            raise serializers.ValidationError({"student": "The student is not actively enrolled in this course."})
        return attrs

    def create(self, validated_data):
        validated_data["recorded_by"] = self.context["request"].user
        return super().create(validated_data)
