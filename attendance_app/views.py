from enum import unique
from django.utils.dateformat import DateFormat
from django.contrib import messages
import openpyxl
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .forms import UploadFileForm, StudentForm, EventForm, DeviceForm
from .models import Student, Attendance, Event, Device, SecurityToken, Day
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from datetime import datetime
import pytz
import json


#TODO duplicate attendances


def students(request):

    students = Student.objects.filter(owner=request.user)

    context = {"students":students}

    return render(request, 'attendance_app/students.html', context)



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


def delete_student(request, student_id):
    student = Student.objects.get(id=student_id)

    Student.objects.filter(id=student_id).delete()
    name = f"{student.last_name}, {student.first_name}, {student.middle_name}"

    context = {"name":name}

    return render(request, "attendance_app/delete_student.html", context)


def delete_device(request, device_id):
    device = Device.objects.get(id=device_id)

    events1 = device.event_set.all()

    context = {"device": device, "events": events1}

    Device.objects.filter(id=device_id).delete()




    return render(request, "attendance_app/delete_device.html",context)


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['files']
            wb = openpyxl.load_workbook(excel_file)
            sheet = wb.active

            for row in sheet.iter_rows(min_row=2, values_only=True):
                card_uid, last_name, first_name, middle_name, student_id = row
                if None in row:
                    continue


                #if not already in database
                #create Student
                if not Student.objects.filter(card_uid=str(card_uid).upper()).exists():

                    Student.objects.create(owner=request.user,card_uid=str(card_uid).upper(), last_name=str(last_name).upper(),
                                           first_name=str(first_name).upper(), middle_name=str(middle_name).upper(), student_id=student_id)

            return redirect('students')
    else:
        form = UploadFileForm()

    return render(request, 'attendance_app/upload.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('index')

def control_panel(request):
    if request.method=="POST":
        admin = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=admin,password=password)


        if user is not None:
            login(request, user)
            return render(request, 'attendance_app/control_panel.html')
        else:
            messages.error(request,"Wrong admin or password")
            return redirect("index")
    return redirect("index")


def attendance_for_today(request, day_id):
    day = Day.objects.get(id=day_id)
    event1 = day.event
    attendances = day.attendance_set.all()

    unique_att = get_unique_attendances(attendances)

    context = {"day":day,
               "event":event1,
               "attendances":unique_att,
               "top":len(unique_att),
               "below":len(Student.objects.all())}

    return render(request, "attendance_app/attendance_for_today.html", context)


def student_attendance(request, student_id):
    student = Student.objects.get(id=student_id)
    attendances = student.attendance_set.all().order_by("-date_attended")

    context = {"attendances":attendances, "student":student}

    return render(request, 'attendance_app/student_attendance.html',context)


def index(request):
    return render(request, 'attendance_app/index.html')



def get_info(request):
    global CurrentUser
    return JsonResponse({'username': CurrentUser[0], "password":CurrentUser[1], 'event_id':CurrentUser[2]})

def dashboard(request):

    user = request.user
    students = user.student_set.all()
    attendances = []
    for student in students:
        attendances.extend(student.attendance_set.all())


    # for attendance in attendances:
    #     print(attendance.date_attended)

    context = {
        "records": attendances
    }

    return render(request, 'attendance_app/dashboard.html', context)


#helper function
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



def add_student(request):
    if request.method != "POST":
        form = StudentForm()
    else:
        form = StudentForm(data=request.POST)
        if form.is_valid():
            new_student = form.save(commit=False)
            new_student.owner = request.user
            new_student.last_name = new_student.last_name.upper()
            new_student.first_name = new_student.first_name.upper()
            new_student.middle_name = new_student.middle_name.upper()
            new_student.card_uid = new_student.card_uid.upper()

            new_student.save()
            return redirect("students")

    return render(request, "attendance_app/add_student.html",{"form":form})


def events(request):
    events1 = Event.objects.all()

    return render(request, "attendance_app/events.html",{"events":events1})


def get_unique_attendances(attendances):
    unique_attendances = {}

    for attendance in attendances:
        if attendance.student.student_id in unique_attendances.keys():
            continue

        unique_attendances[attendance.student.student_id]=attendance


    unique_attendances1 = [i for i in unique_attendances.values()]

    return unique_attendances1


def event(request, event_id):
    event1 = Event.objects.get(id=event_id)


    if request.method=="POST":
        Day.objects.create(date=request.POST.get("date"),event=event1)

    days = event1.day_set.all()

    return render(request, "attendance_app/event.html", {'days':days, "event":event1})


def add_day(request, event_id):

    event1 = Event.objects.get(id=event_id)


    return render(request, "attendance_app/add_day.html", {"event":event1})


def add_event(request):
    if request.method != "POST":
        form = EventForm()
    else:
        form = EventForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("events")

    return render(request, "attendance_app/add_event.html",{"form":form})


def devices(request):
    devices1 = Device.objects.all()

    return render(request, "attendance_app/devices.html",{"devices":devices1})


def add_device(request):
    if request.method != "POST":
        form = DeviceForm()
    else:
        form = DeviceForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("devices")

    return render(request, "attendance_app/add_device.html",{"form":form})


#TODO filter the students with the owner
@csrf_exempt
def api_attendance(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        card_uid = data.get("card_uid")
        token1 = data.get("token")

        try:

            #get the date for the attendance
            current_utc = datetime.now(pytz.utc)
            timezone = pytz.timezone("Asia/Manila")
            current_local = str(current_utc.astimezone(timezone)).split()[0]


            student1 = Student.objects.get(card_uid=str(card_uid).upper())
            token2 = SecurityToken.objects.get(token=token1)
            device1 = Device.objects.get(name=data.get("device"),token=token2)
            event1 = Event.objects.get(device=device1)
            date1 = Day.objects.get(date=current_local, event=event1)

            Attendance.objects.create(student=student1,event=event1,day=date1)
            return JsonResponse({'status': 'success', 'student': str(student1)}, status=201)
        except Student.DoesNotExist:
            return JsonResponse({'status': 'error', 'student': 'Student not found'}, status=404)
        except Event.DoesNotExist:
            return JsonResponse({'status': 'error', 'student': 'Event not found'}, status=404)
        except Device.DoesNotExist:
            return JsonResponse({'status': 'error', 'student': 'Device not found'}, status=404)
        except Day.DoesNotExist:
            return JsonResponse({'status': 'error', 'student': 'Day not registered'}, status=404)
        except SecurityToken.DoesNotExist:
            return JsonResponse({'status': 'error', 'student': 'Token not recognized'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)