from django.urls import path

from . import views



app_name = "attendance_app"
urlpatterns = [
    path('logout/',views.logout_view, name='logout'),
    path("api/",views.api_attendance, name='api_attendance'),
    path("control_panel/",views.control_panel, name='control_panel'),
    path("dashboard/",views.dashboard, name='dashboard'),
    path('delete_device/<int:device_id>/',views.delete_device, name='delete_device'),
    path('date_attendance/',views.date_attendance, name='date_attendance'),
    path("events/",views.events, name='events'),
    path("add_event/",views.add_event, name='add_event'),
    path("event/<int:event_id>/",views.event, name='event'),
    path("devices/",views.devices, name='devices'),
    path("attendance_for_today/<int:day_id>/",views.attendance_for_today, name="attendance_for_today"),
    path("add_day/<int:event_id>/",views.add_day, name='add_day'),
    path("add_device/",views.add_device, name='add_device'),
    path("delete_event/<int:event_id>/",views.delete_event, name='delete_event'),
    path("delete_day/<int:day_id>/",views.delete_day, name='delete_day'),
    path("",views.index, name='index')
]