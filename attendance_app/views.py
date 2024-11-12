from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .forms import EventForm, DeviceForm
from .models import Student, Attendance, Event, Device, SecurityToken, Day
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
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

            current_time = timezone.localtime().time()

            for event in events1:
                if event.start_time > current_time or event.stop_time < current_time:
                    event.status = False
                    event.save()

            return render(request, 'attendance_app/events.html',{"events":events1,"form":form,"curr_time":current_time})
        else:
            messages.error(request,"Wrong admin or password")
            return redirect('attendance_app:index')
    return redirect('attendance_app:index')


def attendance_for_today(request, day_id):
    day = Day.objects.get(id=day_id)
    event1 = day.event
    attendances = []
    for attendance in Attendance.objects.all():
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


def events(request):
    events1 = Event.objects.all()
    form = EventForm()

    current_time = timezone.localtime().time()
    for event in events1:
        if event.start_time > current_time or event.stop_time < current_time:
            event.status = False
            event.save()


    return render(request, "attendance_app/events.html",{"events":events1,"form":form,"curr_time":current_time})


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


def ping_device(request, device_id):
    device = Device.objects.get(id=device_id)

    headers = {
        'Content-Type': 'application/json'
    }

    config_data = {
        "device_name":device.name
    }

    try:
        response = requests.post(f"http://{device.ip_address}/ping",headers=headers,json=config_data, timeout=5)
        device.status = (response.text == "pong")
        print("PONG:",response.text)
        device.save()
    except requests.RequestException:
        device.status = False
        device.save()
    
    return redirect("attendance_app:devices")

def add_device(request):
    if request.method == "POST":
        form = DeviceForm(request.POST)

        if form.is_valid():
            device = form.save(commit=False)
            
            config_data = {
                "ssid": device.ssid,
                "password": device.password_to_ssid,
                "device_name": device.name,
                "apiEndpointUrl": device.apiEndpointUrl
            }

            try:
                headers = {
                    'Content-Type': 'application/json'
                }
                response = requests.post(f"http://{device.ip_address}/config", json=config_data, headers=headers, timeout=5)
            
            except requests.RequestException as e:
                if "timeout=5)" in str(e).split():
                    response = requests.post(f"http://{device.ip_address}/send_ip", json=config_data, headers=headers, timeout=5)

                    if response.status_code == 200:
                        device.ip_address = response.json().get("ip_address")
                        device.status = True
                        device.token = SecurityToken.objects.get(id=1)
                        device.save()

                        return redirect('attendance_app:devices')
                else:
                    form.add_error(None, "Could not connect to ESP32. Exception: {}".format(e))
        else:
            print("Form is invalid:", form.errors)
    else:
        form = DeviceForm()
            
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
        try:
            #get time to check if the attendance got on time
            current_time = timezone.localtime().time()
            
            
            student1 = Student.objects.get(card_uid=str(card_uid).upper())
            token2 = SecurityToken.objects.get(token=token1)
            device1 = Device.objects.get(name=data.get("device"),token=token2)
            event1 = []
            for event in Event.objects.all():
                if event.device==device1:
                    event1.append(event)
            
            
            if len(event1) > 1:
                events_enabled = 0
                for event_i in event1:
                    if event_i.status==True:
                        events_enabled+=1
                        if event_i.start_time <= current_time and event_i.stop_time >= current_time:
                            Attendance.objects.create(student=student1,event=event_i)
                        else:
                            return JsonResponse({'status': 'error', 'message': 'Deadline of Event'}, status=404)
                        
                if events_enabled == 0:
                    return JsonResponse({'status': 'error', 'message': 'Events associated with device disabled'}, status=404)
            else:
                if event1[0].status:
                    if event1[0].start_time <= current_time and event1[0].stop_time >= current_time:
                        Attendance.objects.create(student=student1,event=event1[0])
                    else:
                        return JsonResponse({'status': 'error', 'message': 'Deadline of Event'}, status=404)
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
