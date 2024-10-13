from django import forms
from .models import Event, Device


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
            "name":"Event/Subject",
            "instructor":"Organizer/Instructor"
        }