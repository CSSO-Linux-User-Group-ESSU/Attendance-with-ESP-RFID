from django import forms
from .models import Event, Device
from student_app.models import Course


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['name','ssid','password_to_ssid','apiEndpointUrl','ip_address']
        labels = {
            'name':'Device Name','ssid':'SSID to connect to','password_to_ssid':'Password of SSID','apiEndpointUrl':'API endpoint',
            'ip_address':'IP Address of ESP32'
        }

class EventForm(forms.ModelForm):
    barcode_enabled = forms.BooleanField(required=False, label="Use Barcode Scanner Instead")
    device = forms.ModelChoiceField(
        queryset=Device.objects.all(), 
        required=False,
        label="Select Device (for RFID scanning)"
    )
    # courses = forms.ModelMultipleChoiceField(
    #     queryset=Course.objects.all(),
    #     required=True, 
    #     widget=forms.CheckboxSelectMultiple(),  
    #     label="Select Courses"
    # )

    class Meta:
        model = Event
        fields = ['name', 'instructor', 'device', 'barcode_enabled', 'start_time', 'stop_time']
        labels = {
            "device": "Device",
            "name": "Event/Subject",
            "instructor": "Organizer/Instructor",
            "start_time": "Start Time",
            "stop_time": "Stop Time",
            "barcode_enabled": "Use Barcode Scanner"
        }

        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'stop_time': forms.TimeInput(attrs={'type': 'time'})
        }

    def clean(self):
        cleaned_data = super().clean()
        device = cleaned_data.get("device")
        barcode_enabled = cleaned_data.get("barcode_enabled")
        # courses = cleaned_data.get("courses")

        if not device and not barcode_enabled:
            raise forms.ValidationError("You must select a device or enable barcode scanning.")
        
        # if not courses:
        #     raise forms.ValidationError("At least one course must be selected.")

        return cleaned_data
