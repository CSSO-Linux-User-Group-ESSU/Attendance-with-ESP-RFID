from django.db import models
from student_app.models import Student


# Create your models here.
class SecurityToken(models.Model):
    token = models.CharField(max_length=400, unique=True)

    def __str__(self):
        return self.token


class Device(models.Model):
    name = models.CharField(max_length=200, unique=True)
    token = models.ForeignKey(SecurityToken, on_delete=models.CASCADE)
    ssid = models.CharField(max_length=100)
    password = models.CharField(max_length=200)
    url = models.CharField(max_length=300)

    def __str__(self):
        return self.name


#can be classes
class Event(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, unique=True)
    instructor = models.CharField(max_length=200)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Day(models.Model):
    date = models.DateField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)


    def __str__(self):
        return f"{str(self.date)}"

class Attendance(models.Model):
    # day = models.ForeignKey(Day, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date_attended = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.date_attended}"
