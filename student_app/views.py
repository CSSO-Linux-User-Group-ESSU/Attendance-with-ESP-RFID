from django.shortcuts import render, redirect
from .models import Student
from .forms import UploadFileForm, StudentForm
import openpyxl
import requests
from django.http import JsonResponse
from attendance_app.models import Device


# Create your views here.

def students(request):

    students = Student.objects.all()
    form = StudentForm()
    form1 = UploadFileForm()

    context = {"students":students, "form":form, "form1":form1}


    return render(request, 'student_app/students.html', context)


def delete_student(request, student_id):

    Student.objects.filter(id=student_id).delete()

    return redirect("student_app:students")


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

                    Student.objects.create(card_uid=str(card_uid).upper(), last_name=str(last_name).upper(),
                                           first_name=str(first_name).upper(), middle_name=str(middle_name).upper(), student_id=student_id)

            return redirect('student_app:students')
    else:
        form = UploadFileForm()

    return redirect("student_app:students")


def student_attendance(request, student_id):
    student = Student.objects.get(id=student_id)
    attendances = student.attendance_set.all().order_by("-date_attended")

    context = {"attendances":attendances, "student":student}

    return render(request, 'student_app/student_attendance.html',context)


def add_student(request):
    if request.method != "POST":
        form = StudentForm()
        form1 = UploadFileForm()
    else:
        form = StudentForm(data=request.POST)
        if form.is_valid():
            new_student = form.save(commit=False)
            new_student.card_uid = str(request.POST.get("card_uid")).upper()
            new_student.last_name = new_student.last_name.upper()
            new_student.first_name = new_student.first_name.upper()
            new_student.middle_name = new_student.middle_name.upper()
            new_student.card_uid = new_student.card_uid.upper()

            new_student.save()
            return redirect("student_app:students")

    return render(request, "student_app/students.html",{"form":form,"form1":form1})


def get_card_uid(request):
    
    #get active devices
    devices = Device.objects.all()
    active = []
    for device in devices:
        if device.status:
            active.append(device)
    
    if len(active) < 1:
        print("No device")
        return JsonResponse({'card_uid': 'Error'})

    try:
        response = requests.get(f"http://{active[0].ip_address}/get_card_uid",timeout=5)
        print(response.text)
        return JsonResponse({'card_uid': response.text})
    except requests.RequestException as e:
        print("Exception {}".format(e))
        return JsonResponse({'card_uid': 'Error'})
    

    