from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .models import Student
import json


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


@csrf_exempt
def create_student(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        student = Student.objects.create(
            name=data['name'],
            student_id=data['student_id'],
            department=data['department'],
        )

        return JsonResponse({
            'message': 'Student created successfully',
            'student_id': student.student_id,
        }, status=201)

    return JsonResponse(
        {'error': 'Only POST method is allowed'},
        status=405
    )


def test_create_student(request):
    return HttpResponse("""
        <h2>Create Student</h2>

        <form id="student-form">
            <input name="name" placeholder="Name" required><br>
            <input name="student_id" placeholder="Student ID" required><br>
            <input name="department" placeholder="Department" required><br>
            <button type="submit">Create Student</button>
        </form>

        <p id="result"></p>

        <script>
            const form = document.getElementById('student-form');
            const result = document.getElementById('result');

            form.addEventListener('submit', async function(event) {
                event.preventDefault();

                const formData = new FormData(form);
                const data = Object.fromEntries(formData.entries());

                const response = await fetch('/student/create/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                const resultData = await response.json();
                result.textContent = JSON.stringify(resultData);
            });
        </script>
    """)