from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Assignment, AttendanceRecord, Course, Enrollment, Submission, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Academy profile", {"fields": ("role", "phone", "date_of_birth")}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("Academy profile", {"fields": ("role", "phone", "date_of_birth")}),
    )
    list_display = ("username", "email", "first_name", "last_name", "role", "is_staff")
    list_filter = ("role", "is_staff", "is_active")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "teacher", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "title", "teacher__username")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "status", "enrolled_at")
    list_filter = ("status", "course")
    search_fields = ("student__username", "course__title", "course__code")


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "due_at", "points")
    list_filter = ("course",)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("assignment", "student", "submitted_at", "grade")
    list_filter = ("assignment__course",)


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ("course", "student", "date", "status", "recorded_by")
    list_filter = ("course", "date", "status")
    search_fields = ("student__username", "course__code", "course__title")
