from django.urls import path

from . import views



app_name = "student_app"
urlpatterns = [
    path('upload_file/',views.upload_file, name='upload_file'),
    path('students/',views.students, name='students'),
    path('student_attendance/<int:student_id>/',views.student_attendance, name='student_attendance'),
    path('delete_student/<int:student_id>/',views.delete_student, name='delete_student'),
    path('add_student/',views.add_student, name='add_student'),

]