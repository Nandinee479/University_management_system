from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from .models import Student


def hello(request):
    return HttpResponse("Hello, University Management System!")


def student_info(request):
    students = Student.objects.all()

    data = []
    for student in students:
        data.append({
            'name': student.name,
            'student_id': student.student_id,
            'department': student.department,
        })

    return JsonResponse(data, safe=False)


def student_detail(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)

    data = {
        'name': student.name,
        'student_id': student.student_id,
        'department': student.department,
    }

    return JsonResponse(data)