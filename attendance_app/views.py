from django.contrib import messages
import openpyxl
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .forms import UploadFileForm, StudentForm
from .models import Student, Attendance, Event
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from datetime import datetime
import pytz
import json


global CurrentUser
CurrentUser = ['','','']

def students(request):

    students = Student.objects.filter(owner=request.user)

    context = {"students":students}

    return render(request, 'attendance_app/students.html', context)


def delete_student(request, student_id):
    student = Student.objects.get(id=student_id)

    Student.objects.filter(id=student_id).delete()
    name = f"{student.last_name}, {student.first_name}, {student.middle_name}"

    context = {"name":name}


    return render(request, "attendance_app/delete_student.html", context)


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['files']
            wb = openpyxl.load_workbook(excel_file)
            sheet = wb.active

            for row in sheet.iter_rows(min_row=2, values_only=True):
                card_uid, last_name, first_name, middle_name, student_id = row

                if not Student.objects.filter(card_uid=str(card_uid).upper()).exists():

                    Student.objects.create(owner=request.user,card_uid=str(card_uid).upper(), last_name=str(last_name).upper(), \
                                           first_name=str(first_name).upper(), middle_name=str(middle_name).upper(), student_id=student_id)

            return render(request, 'attendance_app/success.html')
    else:
        form = UploadFileForm()

    return render(request, 'attendance_app/upload.html', {'form': form})


def logout_view(request):
    global CurrentUser
    CurrentUser = ['','','']
    logout(request)
    return redirect('index')

def control_panel(request):
    global CurrentUser
    if request.method=="POST":
        admin = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=admin,password=password)



        if user is not None:
            CurrentUser[0] = admin
            CurrentUser[1] = password
            login(request, user)
            return render(request, 'attendance_app/control_panel.html')
        else:
            messages.error(request,"Wrong admin or password")
            return redirect("index")
    return render(request, 'attendance_app/control_panel.html')


def student_attendance(request, student_id):
    student = Student.objects.get(id=student_id)
    attendances = student.attendance_set.all().order_by("-date_attended")

    context = {"attendances":attendances, "student":student}

    return render(request, 'attendance_app/student_attendance.html',context)


def index(request):
    return render(request, 'attendance_app/index.html')



def get_csrf_token(request):
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


def events(request):
    events1 = Event.objects.all()

    context = {"events":events1}

    return render(request,"attendance_app/events.html",context)


def event(request, event_id):
    global CurrentUser
    event1 = Event.objects.get(id=event_id)

    attendances = event1.attendance_set.all()

    # request.session["selected_event"] = event1.id
    CurrentUser[2] = str(event1.id)

    current_utc = datetime.now(pytz.utc)
    timezone = pytz.timezone("Asia/Manila")
    current_local = current_utc.astimezone(timezone)

    attendances_today = []
    for attendance in attendances:
        if str(attendance.date_attended).split(" ")[0] == str(current_local).split(" ")[0]:
            attendances_today.append(attendance)

    morning_attendances = []
    afternoon_attendances = []

    for attendance in attendances_today:
        if is_morning(attendance.date_attended.astimezone(timezone)):
            morning_attendances.append(attendance)
        else:
            afternoon_attendances.append(attendance)

    context = {
        "morning":morning_attendances,
        "afternoon":afternoon_attendances,
        "event":event1
    }

    return render(request, "attendance_app/event.html",context)


#helper function
def is_morning(date):
    time = str(date).split()[1]

    hour = time.split(":")[0]

    return int(hour) < 12


def attendance_today(request):

    user = request.user
    students = user.student_set.all()
    attendances = []
    for student in students:
        attendances.extend(student.attendance_set.all())

    current_utc = datetime.now(pytz.utc)
    timezone = pytz.timezone("Asia/Manila")
    current_local = current_utc.astimezone(timezone)

    attendances_today = []
    for attendance in attendances:
        if str(attendance.date_attended).split(" ")[0] == str(current_local).split(" ")[0]:
            attendances_today.append(attendance)


    morning_attendances = []
    afternoon_attendances = []

    for attendance in attendances_today:
        if is_morning(attendance.date_attended.astimezone(timezone)):
            morning_attendances.append(attendance)
        else:
            afternoon_attendances.append(attendance)

    context = {
        "morning": morning_attendances,
        "afternoon":afternoon_attendances
    }

    return render(request, 'attendance_app/attendance_today.html', context)

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



@csrf_exempt
def api_attendance(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        card_uid = data.get("card_uid")
        event_id = data.get("event_id")

        user = authenticate(request,username=CurrentUser[0],password=CurrentUser[1])

        try:
            student1 = Student.objects.filter(owner=user).get(card_uid=str(card_uid).upper())
            Attendance.objects.create(student=student1,event=Event.objects.get(id=int(event_id)))
            return JsonResponse({'status': 'success', 'student': str(student1)}, status=201)
        except Student.DoesNotExist:
            return JsonResponse({'status': 'error', 'student': 'Student not found'}, status=404)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'student': 'User not found'}, status=404)
        except Event.DoesNotExist:
            return JsonResponse({'status': 'error', 'student': 'Event not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)