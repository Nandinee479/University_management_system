from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import Student, Course, ClassSchedule, Enrollment
from django.contrib.auth.models import User
from .models import UserProfile
from django.contrib.auth import authenticate, login
from .models import Student 
import json
from django.contrib.auth import login, authenticate

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
def student_courses(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    enrollments = Enrollment.objects.filter(student=student).select_related("course")

    data = []
    for enrollment in enrollments:
        course = enrollment.course
        schedules = course.schedules.all()

        data.append({
            "course_code": course.course_code,
            "title": course.title,
            "credits": course.credits,
            "semester": course.semester,
            "department": course.department,
            "description": course.description,
            "instructor_name": course.instructor_name,
            "instructor_email": course.instructor_email,
            "schedules": [
                {
                    "day": schedule.day,
                    "start_time": schedule.start_time.strftime("%H:%M"),
                    "end_time": schedule.end_time.strftime("%H:%M"),
                    "room": schedule.room,
                }
                for schedule in schedules
            ],
        })

    return JsonResponse(data, safe=False)

@csrf_exempt
def register_user(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST method is allowed"},
            status=405
        )

    try:
        data = json.loads(request.body)
        username = data["username"]
        password = data["password"]
        role = data["role"]
    except (json.JSONDecodeError, KeyError):
        return JsonResponse(
            {"error": "username, password and role are required"},
            status=400
        )

    if role not in ["student", "teacher"]:
        return JsonResponse({"error": "Invalid role"}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "Username already exists"}, status=400)

    user = User.objects.create_user(
        username=username,
        password=password
    )
    UserProfile.objects.create(user=user, role=role)

    return JsonResponse({"message": "Registration successful"}, status=201)


def test_register(request):
    return HttpResponse("""
        <h2>Register Test</h2>
        <input id="username" placeholder="Username"><br><br>
        <input id="password" type="password" placeholder="Password"><br><br>
        <select id="role">
            <option value="student">Student</option>
            <option value="teacher">Teacher</option>
        </select><br><br>
        <button onclick="registerUser()">Register</button>
        <pre id="result"></pre>

        <script>
        async function registerUser() {
            const response = await fetch('/register/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    username: document.getElementById('username').value,
                    password: document.getElementById('password').value,
                    role: document.getElementById('role').value
                })
            });
            document.getElementById('result').textContent =
                await response.text();
        }
        </script>
    """)

@csrf_exempt
def login_user(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST method is allowed"},
            status=405
        )

    try:
        data = json.loads(request.body)
        username = data["username"]
        password = data["password"]
    except (json.JSONDecodeError, KeyError):
        return JsonResponse(
            {"error": "username and password are required"},
            status=400
        )

    user = authenticate(request, username=username, password=password)

    if user is None:
        return JsonResponse(
            {"error": "Invalid username or password"},
            status=401
        )

    login(request, user)
    role = user.userprofile.role

    return JsonResponse({
        "message": "Login successful",
        "username": user.username,
        "role": role
    })


def test_login(request):
    return HttpResponse("""
        <h2>Login Test</h2>
        <input id="username" placeholder="Username"><br><br>
        <input id="password" type="password" placeholder="Password"><br><br>
        <button onclick="loginUser()">Login</button>
        <pre id="result"></pre>

        <script>
        async function loginUser() {
            const response = await fetch('/login/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    username: document.getElementById('username').value,
                    password: document.getElementById('password').value
                })
            });
            document.getElementById('result').textContent =
                await response.text();
        }
        </script>
    """)