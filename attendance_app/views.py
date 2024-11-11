from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .forms import EventForm, DeviceForm
from .models import Student, Attendance, Event, Device, SecurityToken, Day
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from datetime import datetime
import pytz
import requests
import json


def change_status(request, event_id):
    event = Event.objects.get(id=event_id)

    if event.status:
        event.status = False
    else:
        event.status = True

    event.save()
    return redirect("attendance_app:events")

    # events1 = Event.objects.all()
    # form = EventForm()

    # # return render(request, "attendance_app/events.html",{"events":events1,"form":form})


def signup(request):

    if request.method=="POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        password2 = request.POST["password2"]


        if password != password2:
            messages.error(request, "Wrong password confirmation")
            return redirect("attendance_app:signup")
        

        user, created = User.objects.get_or_create(username=username,email=email)


        if created:
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            messages.success(request, "User created")
            return render(request, "attendance_app/index.html")

        else:
            messages.error(request,"User already exists")
            return redirect("attendance_app:signup")

    return render(request, "attendance_app/signup.html")


def date_attendance(request):

    if request.method=="POST":
        date = request.POST.get("date")
        attendances = Attendance.objects.all()
        attendance_for_date = []
        for attendance in attendances:
            date_attended = str(attendance.date_attended).split()[0]
            if date==date_attended:
                attendance_for_date.append(attendance)

        return render(request,"attendance_app/date_attendance.html",{"date":str(date), "attendances":attendance_for_date})
    
    return render(request,"attendance_app/date_attendance.html")


def delete_device(request, device_id):
    Device.objects.filter(id=device_id).delete()
    return redirect("attendance_app:devices")


def logout_view(request):
    logout(request)
    return redirect("attendance_app:index")


def control_panel(request):
    if request.method=="POST":
        admin = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=admin,password=password)

        if user is not None:
            login(request, user)
            events1 = Event.objects.all()
            form = EventForm()
            return render(request, 'attendance_app/events.html',{"events":events1,"form":form})
        else:
            messages.error(request,"Wrong admin or password")
            return redirect('attendance_app:index')
    return redirect('attendance_app:index')


def attendance_for_today(request, day_id):
    day = Day.objects.get(id=day_id)
    event1 = day.event
    # attendances = day.attendance_set.all()
    attendances = []
    for attendance in Attendance.objects.all():
        # print(str(attendance.date_attended).split()[0])
        # print(day.date)
        if str(attendance.date_attended).split()[0] == str(day.date):
            attendances.append(attendance)

    unique_att = get_unique_attendances(attendances)

    context = {"day":day,
               "event":event1,
               "attendances":unique_att,
               "top":len(unique_att),
               "below":len(Student.objects.all())}

    return render(request, "attendance_app/attendance_for_today.html", context)


def index(request):
    return render(request, 'attendance_app/index.html')


def dashboard(request):

    attendances = Attendance.objects.all()
    context = {
        "records": attendances
    }

    return render(request, 'attendance_app/dashboard.html', context)


def is_morning(date):
    time = str(date).split()[1]

    hour = time.split(":")[0]

    return int(hour) < 12


def get_morning_afternoon(attendances):
    timezone = pytz.timezone("Asia/Manila")


    morning_attendances = []
    afternoon_attendances = []

    for attendance in attendances:
        if is_morning(attendance.date_attended.astimezone(timezone)):
            morning_attendances.append(attendance)
        else:
            afternoon_attendances.append(attendance)

    return morning_attendances, afternoon_attendances


def events(request):
    events1 = Event.objects.all()
    form = EventForm()

    return render(request, "attendance_app/events.html",{"events":events1,"form":form})


def get_unique_attendances(attendances):
    unique_attendances = {}

    for attendance in attendances:
        if attendance.student.student_id in unique_attendances.keys():
            continue

        unique_attendances[attendance.student.student_id]=attendance


    unique_attendances1 = [i for i in unique_attendances.values()]

    return unique_attendances1

#used in event view for displaying the days with attendances
def get_days_of_attendances(attendances, event_id):
    for attendance in attendances:
        if attendance.event==Event.objects.get(id=event_id):
            date = str(attendance.date_attended).split()[0]
            event = Event.objects.get(id=event_id)
            Day.objects.get_or_create(date=date, event=event)

    

def event(request, event_id):
    event1 = Event.objects.get(id=event_id)
    get_days_of_attendances(Attendance.objects.all(), event_id)

    # if request.method=="POST":
    #     day, created = Day.objects.get_or_create(date=request.POST.get("date"), event=event1)

    #     if created:
    #         pass
    #     else:
    #         messages.error(request,"Date already exists")
    #         days = event1.day_set.all()
            
    #         return render(request, "attendance_app/event.html", {'days':days, "event":event1 })

    days = event1.day_set.all()

    return render(request, "attendance_app/event.html", {'days':days, "event":event1})


def add_event(request):
    if request.method != "POST":
        form = EventForm()
    else:
        form = EventForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("attendance_app:events")

    return render(request, "attendance_app/events.html",{"form":form})


def devices(request):
    devices1 = Device.objects.all()
    form = DeviceForm()

    return render(request,"attendance_app/devices.html",{"devices":devices1,"form":form})


import requests
from django.shortcuts import redirect, render
from .forms import DeviceForm

def add_device(request):
    print("METHOD:", request.method)
    
    if request.method == "POST":
        form = DeviceForm(request.POST)
        print("Form submitted with POST data:", request.POST)

        if form.is_valid():
            print("Form is valid.")
            device = form.save(commit=False)
            
            config_data = {
                "ssid": device.ssid,
                "password": device.password_to_ssid,
                "device_name": device.name,
                "apiEndpointUrl": device.apiEndpointUrl
            }

            print("Config data prepared for ESP32:", config_data)
            
            try:
                # Print out the exact URL to verify if it's correct
                print(f"Attempting to send config data to: {device.ip_address}/config")
                headers = {
                    'Content-Type': 'application/json'
                }
                response = requests.post(f"http://{device.ip_address}/config", json=config_data, headers=headers, timeout=120)

                print(response)
                
                print("Received response from ESP32. Status code:", response.status_code)
                print("Response content:", response.content)

                if response.status_code == 200:
                    # Extract and print the IP address if returned
                    device.ip_address = response.json().get("ip_address")
                    device.status = True
                    device.token = SecurityToken.objects.get(id=1)
                    device.save()
                    print("Device configured successfully. Redirecting...")

                    return redirect('attendance_app:devices')
                else:
                    print("ESP32 responded, but status code is not 200.")
                    form.add_error(None, "Failed to configure the ESP32. Status code: {}".format(response.status_code))
            
            except requests.RequestException as e:
                print("Exception occurred:", e)
                form.add_error(None, "Could not connect to ESP32. Exception: {}".format(e))
        else:
            print("Form is invalid:", form.errors)
    else:
        form = DeviceForm()
            
    print("Rendering form with errors (if any).")
    return render(request, "attendance_app/devices.html", {"form": form})



def delete_event(request, event_id):
    Event.objects.get(id=event_id).delete()

    return redirect("attendance_app:events")


def delete_day(request, event_id):

    events = Event.objects.get(id=event_id)

    attendances = events.attendance_set.all()
    days = events.day_set.all()

    for attendance in attendances:
        attendance.delete()
    
    for day in days:
        day.delete()

    return redirect("attendance_app:events")


@csrf_exempt
def api_attendance(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        card_uid = data.get("card_uid")
        token1 = data.get("token")
        # ping = data.get("ping")

        try:
            #get the date for the attendance
            # current_utc = datetime.now(pytz.utc)
            # timezone = pytz.timezone("Asia/Manila")
            # current_local = str(current_utc.astimezone(timezone)).split()[0]


            student1 = Student.objects.get(card_uid=str(card_uid).upper())
            token2 = SecurityToken.objects.get(token=token1)
            device1 = Device.objects.get(name=data.get("device"),token=token2)
            event1 = []
            for event in Event.objects.all():
                if event.device==device1:
                    event1.append(event)
            # date1 = Day.objects.get(date=current_local, event=event1)

            if len(event1) > 1:
                events_enabled = 0
                for event_i in event1:
                    if event_i.status:
                        events_enabled+=1
                        Attendance.objects.create(student=student1,event=event_i)
                if events_enabled == 0:
                    return JsonResponse({'status': 'error', 'message': 'Events associated with device disabled'}, status=404)
            else:
                if event_i.status:
                    Attendance.objects.create(student=student1,event=event1)
                else:
                    return JsonResponse({'status': 'error', 'message': 'Event disabled'}, status=404)
                
            #success
            return JsonResponse({'status': 'success', 'student': str(student1)}, status=201)
        except Student.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Student not found'}, status=404)
        except Event.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Event not found'}, status=404)
        except Device.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Device not found'}, status=404)
        except SecurityToken.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Token not recognized'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
