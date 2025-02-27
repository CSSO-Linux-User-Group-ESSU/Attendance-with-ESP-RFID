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

class EventForm(forms.ModelForm):
    barcode_enabled = forms.BooleanField(required=False, label="Use Barcode Scanner Instead")
    device = forms.ModelChoiceField(
        queryset=Device.objects.all(), 
        required=False,  # Allow empty selection
        label="Select Device (for RFID scanning)"
    )
    
    class Meta:
        model = Event
        fields = ['name', 'instructor', 'device', 'barcode_enabled', 'start_time', 'stop_time']
        labels = {
            "device": "Device",
            "name":"Event/Subject",
            "instructor":"Organizer/Instructor",
            "start_time":"Start Time",
            "stop_time":"Stop Time",
            "barcode_enabled":"Use Barcode Scanner"
        }

        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'stop_time': forms.TimeInput(attrs={'type': 'time'})
        }

    def clean(self):
        cleaned_data = super().clean()
        device = cleaned_data.get("device")
        barcode_enabled = cleaned_data.get("barcode_enabled")

        if not device and not barcode_enabled:
            raise forms.ValidationError("You must select a device or enable barcode scanning.")
        
        return cleaned_data