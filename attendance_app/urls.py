from django.urls import path

from . import views

urlpatterns = [
    path('upload/',views.upload_file, name='upload_file'),
    path('logout/',views.logout_view, name='logout'),
    path("api/",views.api_attendance, name='api_attendance'),
    path("control_panel/",views.control_panel, name='control_panel'),
    path("dashboard/",views.dashboard, name='dashboard'),
    path('students/',views.students, name='students'),
    path('student_attendance/<int:student_id>/',views.student_attendance, name='student_attendance'),
    path('delete_student/<int:student_id>/',views.delete_student, name='delete_student'),
    path("",views.index, name='index')
]