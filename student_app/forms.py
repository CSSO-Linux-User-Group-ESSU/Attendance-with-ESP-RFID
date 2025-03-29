from django import forms
from .models import Student, Course

class UploadFileForm(forms.Form):
    files = forms.FileField()


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['last_name', 'middle_name', 'first_name', 'student_id','course']

        labels = {
            'last_name': 'Last Name',
            'middle_name': 'Middle Name',
            'first_name': 'First Name',
            'student_id': 'Student ID',
            'course': 'Course'
        }

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name']

        labels = {
            'name': 'Course Name'
        }
