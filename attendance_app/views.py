from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .forms import EventForm, DeviceForm
from .models import Student, Attendance, Event, Device, SecurityToken
from student_app.models import Course
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
import requests
import json


def student_courses(request, course_id):
    course = Course.objects.get(id=course_id)
    students = Student.objects.filter(course=course)

    context = {"students":students, 'course':course}


    return render(request, 'attendance_app/students_courses.html', context)

@login_required
def courses(request):
    courses1 = Course.objects.all()

    

    return render(
        request,
        "attendance_app/courses.html",
        {
            "courses": courses1
        },
    )

def log_in(request):
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect(
                "attendance_app:events"
            )  # Redirect to the home page or dashboard
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "attendance_app/log_in.html")


def signup(request):
    # print("Hello")
    if request.method == "POST":
        # print("HGello")
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        password2 = request.POST["password2"]

        if password != password2:
            messages.error(request, "Wrong password confirmation")
            return redirect("attendance_app:signup")

        user, created = User.objects.get_or_create(username=username, email=email)

        if created:
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            messages.success(request, "User created")
            return render(request, "attendance_app/log_in.html")

        else:
            messages.error(request, "User already exists")
            return redirect("attendance_app:signup")

    return render(request, "attendance_app/signup.html")


def logout_view(request):
    logout(request)
    return redirect("attendance_app:log_in")


def home(request):
    return render(request, "attendance_app/home.html")


def update_profile(request):
    if request.method == "POST":
        user = request.user

        user.last_name = request.POST.get("last_name", user.last_name)
        user.first_name = request.POST.get("first_name", user.first_name)
        user.username = request.POST.get("username", user.username)
        user.email = request.POST.get("email", user.email)
        # password = request.POST.get('password')

        # if password:
        #     user.set_password(password)

        user.save()

        login(request, user)

        return redirect("attendance_app:events")


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


@login_required
def date_attendance(request):

    if request.method == "POST":
        date = request.POST.get("date")
        attendances = Attendance.objects.all()
        attendance_for_date = []
        for attendance in attendances:
            date_attended = str(attendance.date_attended).split()[0]
            if date == date_attended:
                attendance_for_date.append(attendance)

        return render(
            request,
            "attendance_app/date_attendance.html",
            {"date": str(date), "attendances": attendance_for_date},
        )

    return render(request, "attendance_app/date_attendance.html")


def delete_device(request, device_id):
    Device.objects.filter(id=device_id).delete()
    return redirect("attendance_app:devices")


@login_required
def control_panel(request):
    if request.method == "POST":
        admin = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=admin, password=password)

        if user is not None:
            login(request, user)
            events1 = Event.objects.all()
            form = EventForm()

            current_time = timezone.localtime().time()
            current_date = timezone.now().date()
            for event in events1:
                if current_date != event.date_added:
                    event.status = False
                    event.save()
                    continue
                if event.start_time > current_time or event.stop_time < current_time:
                    event.status = False
                    event.save()

            return render(
                request,
                "attendance_app/events.html",
                {
                    "events": events1,
                    "form": form,
                    "curr_time": current_time,
                    "curr_date": current_date,
                },
            )
        else:
            messages.error(request, "Wrong admin or password")
            return redirect("attendance_app:log_in")
    return redirect("attendance_app:log_in")


@login_required
def attendance_for_today(request, event_id):
    event1 = Event.objects.get(id=event_id)
    attendances = []
    for attendance in Attendance.objects.all():
        if (
            str(attendance.date_attended).split()[0] == str(event1.date_added)
            and attendance.event == event1
        ):
            attendances.append(attendance)

    unique_att = get_unique_attendances(attendances)

    context = {
        "day": event1.date_added,
        "event": event1,
        "attendances": unique_att,
        "top": len(unique_att),
        "below": len(Student.objects.all()),
    }

    return render(request, "attendance_app/attendance_for_today.html", context)


@login_required
def dashboard(request):

    attendances = Attendance.objects.all()
    context = {"records": attendances}

    return render(request, "attendance_app/dashboard.html", context)


@login_required
def events(request):
    events1 = Event.objects.all()
    form = EventForm()
    courses = Course.objects.all()

    current_time = timezone.localtime().time()
    current_date = timezone.now().date()

    for event in events1:
        if current_date != event.date_added:
            event.status = False
            event.save()
            continue
        if event.start_time > current_time or event.stop_time < current_time:
            event.status = False
            event.save()

    return render(
        request,
        "attendance_app/events.html",
        {
            "events": events1,
            "form": form,
            "courses":courses,
            "curr_time": current_time,
            "curr_date": current_date,
        },
    )


def get_unique_attendances(attendances):
    unique_attendances = {}

    for attendance in attendances:
        if attendance.student.student_id in unique_attendances.keys():
            continue

        unique_attendances[attendance.student.student_id] = attendance

    unique_attendances1 = [i for i in unique_attendances.values()]

    return unique_attendances1


def add_event(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        courses = Course.objects.all()
        selected_courses = request.POST.getlist("courses")
        if form.is_valid():
            event = form.save(commit=False)

            event_name = event.name
            instructor = event.instructor
            event_stt = event.start_time
            event_stop = event.stop_time


            # If barcode is enabled, remove device association
            if form.cleaned_data.get("barcode_enabled"):
                event.device = None
            event = Event.objects.create(name=event_name, instructor=instructor, stop_time=event_stop,start_time=event_stt)
            event.courses.set(Course.objects.filter(id__in=selected_courses))

            event.save()
            return redirect("attendance_app:events")

    else:
        form = EventForm()
        courses = Course.objects.all()
    return render(request, "attendance_app/events.html", {"form": form, "courses":courses})


@login_required
def devices(request):
    devices1 = Device.objects.all()
    form = DeviceForm()

    return render(
        request, "attendance_app/devices.html", {"devices": devices1, "form": form}
    )


def ping_device(request, device_id):
    device = Device.objects.get(id=device_id)

    headers = {"Content-Type": "application/json"}

    config_data = {"device_name": device.name}

    try:
        response = requests.post(
            f"http://{device.ip_address}/ping",
            headers=headers,
            json=config_data,
            timeout=5,
        )
        device.status = response.text == "pong"
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
                "apiEndpointUrl": device.apiEndpointUrl,
            }

            try:
                headers = {"Content-Type": "application/json"}
                response = requests.post(
                    f"http://{device.ip_address}/config",
                    json=config_data,
                    headers=headers,
                    timeout=5,
                )

            except requests.RequestException as e:
                if "timeout=5)" in str(e).split():
                    response = requests.post(
                        f"http://{device.ip_address}/send_ip",
                        json=config_data,
                        headers=headers,
                        timeout=5,
                    )

                    if response.status_code == 200:
                        device.ip_address = response.json().get("ip_address")
                        device.status = True
                        device.token = SecurityToken.objects.get(id=1)
                        device.save()

                        return redirect("attendance_app:devices")
                else:
                    form.add_error(
                        None, "Could not connect to ESP32. Exception: {}".format(e)
                    )
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
    if request.method == "POST":
        data = json.loads(request.body)
        card_uid = data.get("card_uid")
        barcode = data.get("barcode")
        token1 = data.get("token")
        event_taken = data.get("event")
        barcode_enabled = barcode is not None and barcode != ""

        try:
            # get time to check if the attendance got on time
            current_time = timezone.localtime().time()

            if barcode_enabled:
                student1 = Student.objects.get(student_id=str(barcode.strip()))
                student_course = student1.course
                event1 = [Event.objects.get(name=str(event_taken))]
            else:
                if not token1:
                    return JsonResponse({"status": "Error", "message": "Token required for RFID scans"}, status=400)
                student1 = Student.objects.get(card_uid=str(card_uid).upper())
                student_course = student1.course
                token2 = SecurityToken.objects.get(token=token1)
                event1 = []
                device1 = Device.objects.get(name=data.get("device"), token=token2)
                for event in Event.objects.all():
                    if event.device == device1:
                        event1.append(event)

            if len(event1) == 0:
                return JsonResponse(
                    {"status": "Error", "message": "No Events"}, status=404
                )

            if len(event1) > 1:
                events_enabled = 0
                for event_i in event1:
                    if event_i.status == True:
                        events_enabled += 1
                        #check if student course is allowed in the event
                        allowed_courses = [event_course.id for event_course in event_i.courses.all()]
                        if student_course.id not in allowed_courses:
                            return JsonResponse(
                                {"status": "Error", "message": "Student Course not allowed in Event"},
                                status=404,
                            )

                        if (
                            event_i.start_time <= current_time
                            and event_i.stop_time >= current_time
                        ):
                            Attendance.objects.create(student=student1, event=event_i)
                        else:
                            return JsonResponse(
                                {"status": "Error", "message": "Event Deadline"},
                                status=404,
                            )

                if events_enabled == 0:
                    return JsonResponse(
                        {"status": "Error", "message": "No Events"}, status=404
                    )
            else:
                if event1[0].status:
                    allowed_courses = [event_course.id for event_course in event1[0].courses.all()]
                    if student_course.id not in allowed_courses:
                        return JsonResponse(
                            {"status": "Error", "message": "Student Course not allowed in Event"},
                            status=404,
                        )
                    if (
                        event1[0].start_time <= current_time
                        and event1[0].stop_time >= current_time
                    ):
                        Attendance.objects.create(student=student1, event=event1[0])
                    else:
                        return JsonResponse(
                            {"status": "Error", "message": "Event Deadline"}, status=404
                        )
                else:
                    return JsonResponse(
                        {"status": "Error", "message": "Event disabled"}, status=404
                    )

            # success
            return JsonResponse(
                {"status": "Success", "message": str(student1)}, status=201
            )
        except Student.DoesNotExist:
            return JsonResponse(
                {"status": "Error", "message": "Student Denied"}, status=404
            )
        except Event.DoesNotExist:
            return JsonResponse({"status": "Error", "message": "No Event"}, status=404)
        except Device.DoesNotExist:
            return JsonResponse({"status": "Error", "message": "No Device"}, status=404)
        except SecurityToken.DoesNotExist:
            if not barcode_enabled:
                return JsonResponse(
                    {"status": "Error", "message": "Token unknown"}, status=404
                )
    return JsonResponse({"status": "Error", "message": "Invalid request"}, status=400)
