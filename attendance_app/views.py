from django.contrib import messages
import openpyxl
from django.shortcuts import render, redirect
from .forms import UploadFileForm
from .models import Student, Attendance
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import time
from django.contrib.auth import authenticate, login, logout


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['files']
            wb = openpyxl.load_workbook(excel_file)
            sheet = wb.active

            for row in sheet.iter_rows(min_row=2, values_only=True):
                card_uid, last_name, first_name, middle_name, student_id = row

                if not Student.objects.filter(card_uid=card_uid).exists():
                    Student.objects.create(card_uid=card_uid, last_name=last_name, first_name=first_name, middle_name=middle_name, student_id=student_id)

            return render(request, 'attendance_app/success.html')
    else:
        form = UploadFileForm()

    return render(request, 'attendance_app/upload.html', {'form': form})


def go_back(request):
    return redirect("control_panel")

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
    return render(request, 'attendance_app/control_panel.html')

def index(request):
    return render(request, 'attendance_app/index.html')


def dashboard(request):
    # Define the time ranges for morning and afternoon
    morning_start = time(0, 0, 0)
    morning_end = time(11, 59, 59)
    afternoon_start = time(12, 0, 0)

    all_records = Attendance.objects.all().order_by('-date_attended')

    morning_records = []
    afternoon_records = []
    seen_students_morning = set()
    seen_students_afternoon = set()

    for record in all_records:
        if morning_start <= record.date_attended.time() <= morning_end:
            if record.student not in seen_students_morning:
                morning_records.append(record)
                seen_students_morning.add(record.student)
        elif record.date_attended.time() >= afternoon_start:
            if record.student not in seen_students_afternoon:
                afternoon_records.append(record)
                seen_students_afternoon.add(record.student)

    context = {
        "morning_records": morning_records,
        "afternoon_records": afternoon_records
    }

    return render(request, 'attendance_app/dashboard.html', context)

@csrf_exempt
def api_attendance(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        card_uid = data.get('card_uid')
        try:
            student1 = Student.objects.get(card_uid=card_uid)
            Attendance.objects.create(student=student1)
            return JsonResponse({'status': 'success', 'student': str(student1)}, status=201)
        except Student.DoesNotExist:
            return JsonResponse({'status': 'error', 'student': 'Student not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

