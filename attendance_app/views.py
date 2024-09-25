from django.shortcuts import render

# Create your views here.
import openpyxl
from django.shortcuts import render
from .forms import UploadFileForm
from .models import Student
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json



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

@csrf_exempt
def api_attendance(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        card_uid = data.get('card_uid')
        try:
            student1 = Student.objects.get(card_uid=card_uid)
            return JsonResponse({'status': 'success', 'student': str(student1)}, status=201)
        except Student.DoesNotExist:
            return JsonResponse({'status': 'error', 'student': 'Student not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

