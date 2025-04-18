from django.db import models

# Create your models here.

class Course(models.Model):
    name = models.CharField(max_length=500, unique=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    card_uid = models.CharField(max_length=100, blank=True,null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=8, unique=True)

    def __str__(self):
        return f"{self.last_name}, {self.first_name}, {self.middle_name}"


