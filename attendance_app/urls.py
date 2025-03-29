from django.urls import path
from . import views


app_name = "attendance_app"
urlpatterns = [
    path("ping_device/<int:device_id>/", views.ping_device, name="ping_device"),
    path("update_profile/", views.update_profile, name="update_profile"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("api/", views.api_attendance, name="api_attendance"),
    path("control_panel/", views.control_panel, name="control_panel"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("delete_device/<int:device_id>/", views.delete_device, name="delete_device"),
    path("date_attendance/", views.date_attendance, name="date_attendance"),
    path("events/", views.events, name="events"),
    path("courses/", views.courses, name="courses"),
    path("student_courses/<int:course_id>", views.student_courses, name="student_courses"),
    path("add_event/", views.add_event, name="add_event"),
    path("devices/", views.devices, name="devices"),
    path(
        "attendance_for_today/<int:event_id>/",
        views.attendance_for_today,
        name="attendance_for_today",
    ),
    path("add_device/", views.add_device, name="add_device"),
    path("delete_event/<int:event_id>/", views.delete_event, name="delete_event"),
    path("delete_day/<int:event_id>/", views.delete_day, name="delete_day"),
    path("change_status/<int:event_id>/", views.change_status, name="change_status"),
    path("", views.log_in, name="log_in"),
    path("home", views.home, name="home"),
]
