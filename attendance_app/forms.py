from django import forms
from .models import Event, Device


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['name','ssid','password_to_ssid','apiEndpointUrl','ip_address']
        labels = {
            'name':'Device Name','ssid':'SSID to connect to','password_to_ssid':'Password of SSID','apiEndpointUrl':'API endpoint',
            'ip_address':'IP Address of ESP32'
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['device', 'name', 'instructor', 'start_time', 'stop_time']

        labels = {
            "device": "Device",
            "name":"Event/Subject",
            "instructor":"Organizer/Instructor",
            "start_time":"Start Time",
            "stop_time":"Stop Time"
        }

        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'stop_time': forms.TimeInput(attrs={'type': 'time'})
        }