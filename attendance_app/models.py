from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Student(models.Model):
    card_uid = models.CharField(max_length=100)

    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=8)
    owner = models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.last_name}, {self.first_name}, {self.middle_name}"

# class ESSUEvent(models.Model):
#     name = models.CharField(max_length=100)
#     when = models.CharField(max_length=100)
#     where = models.CharField(max_length=200)
#     description = models.TextField()
#
#
#     def __str__(self):
#         return self.name

class Event(models.Model):
    name = models.CharField(max_length=100)
    when = models.CharField(max_length=100)
    where = models.CharField(max_length=200)
    description = models.TextField()


    def __str__(self):
        return self.name


class Attendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date_attended = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.student} - {self.date_attended}"


