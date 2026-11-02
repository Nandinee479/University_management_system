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

        if Student.objects.filter(student_id=data['student_id']).exists():
            return JsonResponse({
                'error': 'This student ID already exists'
            }, status=400)

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
@csrf_exempt
def update_student(request, student_id):
    if request.method == 'PUT':
        student = get_object_or_404(Student, student_id=student_id)
        data = json.loads(request.body)

        student.name = data['name']
        student.department = data['department']
        student.save()

        return JsonResponse({
            'message': 'Student updated successfully',
            'student_id': student.student_id,
        })

    return JsonResponse(
        {'error': 'Only PUT method is allowed'},
        status=405
    )


@csrf_exempt
def delete_student(request, student_id):
    if request.method == 'DELETE':
        student = get_object_or_404(Student, student_id=student_id)
        student.delete()

        return JsonResponse({
            'message': 'Student deleted successfully',
            'student_id': student_id,
        })

    return JsonResponse(
        {'error': 'Only DELETE method is allowed'},
        status=405
    )
def test_delete_student(request):
    return HttpResponse("""
        <h2>Delete Student</h2>

        <form id="delete-form">
            <input name="student_id" placeholder="Student ID" required>
            <button type="submit">Delete Student</button>
        </form>

        <p id="result"></p>

        <script>
            const form = document.getElementById('delete-form');
            const result = document.getElementById('result');

            form.addEventListener('submit', async function(event) {
                event.preventDefault();

                const studentId = new FormData(form).get('student_id');

                const response = await fetch(
                    `/student/${studentId}/delete/`,
                    { method: 'DELETE' }
                );

                const responseText = await response.text();
                result.textContent = 'HTTP ' + response.status + ': ' + responseText;
            });
        </script>
    """)
def test_update_student(request):
    return HttpResponse("""
        <h2>Update Student</h2>

        <form id="update-form">
            <input name="student_id" placeholder="Student ID" required><br>
            <input name="name" placeholder="New name" required><br>
            <input name="department" placeholder="New department" required><br>
            <button type="submit">Update Student</button>
        </form>

        <p id="result"></p>

        <script>
    const form = document.getElementById('update-form');
    const result = document.getElementById('result');

    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        result.textContent = 'Updating...';

        try {
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            const studentId = data.student_id;
            delete data.student_id;

            const response = await fetch(`/student/${studentId}/update/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const responseText = await response.text();
            result.textContent = 'HTTP ' + response.status + ': ' + responseText; 
        } catch (error) {
            result.textContent = 'Request failed: ' + error.message;
        }
    });
</script>
    """)