from django import forms
from .models import Student, Event, Device


class UploadFileForm(forms.Form):
    files = forms.FileField()


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['card_uid', 'last_name', 'middle_name', 'first_name', 'student_id']

        labels = {
            'card_uid': 'Card UID',
            'last_name': 'Last Name',
            'middle_name': 'Middle Name',
            'first_name': 'First Name',
            'student_id': 'Student ID',
        }


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['name','token']

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['device', 'name', 'instructor']

        labels = {
            "device": "Device",
            "name":"Event/Subject Name",
            "instructor":"Organizer/Instructor"
        }