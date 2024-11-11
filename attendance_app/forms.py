from django import forms
from .models import Event, Device


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['name','ssid','password_to_ssid','url']
        labels = {
            'name':'Device Name','ssid':'SSID to connect to','password_to_ssid':'Password of SSID','url':'API endpoint'
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['device', 'name', 'instructor']

        labels = {
            "device": "Device",
            "name":"Event/Subject",
            "instructor":"Organizer/Instructor"
        }