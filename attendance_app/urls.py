from django.urls import path

from . import views

urlpatterns = [
    path('',views.upload_file, name='upload_file'),
    path("api/",views.api_attendance, name='api_attendance')
]