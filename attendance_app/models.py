from django.db import models
from student_app.models import Student, Course


# Create your models here.
class SecurityToken(models.Model):
    token = models.CharField(max_length=400, unique=True)

    def __str__(self):
        return self.token


class Device(models.Model):
    name = models.CharField(max_length=200, unique=True)
    token = models.ForeignKey(SecurityToken, on_delete=models.CASCADE)
    ssid = models.CharField(max_length=100)
    password_to_ssid = models.CharField(max_length=200)
    apiEndpointUrl = models.CharField(max_length=300)
    ip_address = models.CharField(max_length=50)
    status = models.BooleanField()
    barcode_enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.name


#can be classes
class Event(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE,null=True,blank=True)
    courses = models.ManyToManyField(Course, related_name='events')
    name = models.CharField(max_length=200, unique=True)
    instructor = models.CharField(max_length=200)
    status = models.BooleanField(default=True)
    start_time = models.TimeField()
    stop_time = models.TimeField()
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name
    


class Attendance(models.Model):
    # day = models.ForeignKey(Day, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date_attended = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.date_attended}"
