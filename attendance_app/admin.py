from django.contrib import admin
from .models import Attendance, Event, Device, SecurityToken

# Register your models here.
admin.site.register(Attendance)
admin.site.register(Event)
admin.site.register(Device)
admin.site.register(SecurityToken)