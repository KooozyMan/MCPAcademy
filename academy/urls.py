from rest_framework.routers import DefaultRouter

from .views import (
    AssignmentViewSet,
    AttendanceViewSet,
    CourseViewSet,
    EnrollmentViewSet,
    SubmissionViewSet,
)

router = DefaultRouter()
router.register("courses", CourseViewSet, basename="course")
router.register("enrollments", EnrollmentViewSet, basename="enrollment")
router.register("assignments", AssignmentViewSet, basename="assignment")
router.register("submissions", SubmissionViewSet, basename="submission")
router.register("attendance", AttendanceViewSet, basename="attendance")

urlpatterns = router.urls
