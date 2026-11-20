from functools import wraps
import json

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .models import Enrollment, Student, UserProfile

def login_required_api(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {"error": "Please login first"},
                status=401
            )
        return view_func(request, *args, **kwargs)
    return wrapper

def hello(request):
    return HttpResponse("Hello, University Management System!")

@login_required_api
def student_info(request):
    students = Student.objects.all()
    search = request.GET.get('search')
    department = request.GET.get('department')
    status = request.GET.get('status')

    if search:
        students = students.filter(
            name__icontains=search
        ) | students.filter(
            student_id__icontains=search
        )

    if department:
        students = students.filter(department__iexact=department)

    if status:
        students = students.filter(status=status)

    data = []
    for student in students:
        data.append({
            'name': student.name,
            'student_id': student.student_id,
            'department': student.department,
            'semester': student.semester,
            'status': student.status,
            'courses': list(
                Enrollment.objects.filter(student=student)
                .values_list('course__title', flat=True)
            ),
        })

    return JsonResponse(data, safe=False)

def student_detail(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)

    data = {
        'name': student.name,
        'student_id': student.student_id,
        'department': student.department,
        'semester': student.semester,
        'status': student.status,
    }

    return JsonResponse(data)

@csrf_exempt
@login_required_api
def create_student(request):
    if request.method != 'POST':
        return JsonResponse(
            {'error': 'Only POST method is allowed'},
            status=405
        )

    try:
        data = json.loads(request.body)

        name = data.get('name')
        student_id = data.get('student_id')
        department = data.get('department')
        semester = data.get('semester')
        status = data.get('status', 'active')

        if not all([name, student_id, department, semester]):
            return JsonResponse(
                {'error': 'All required fields must be provided'},
                status=400
            )

        if not isinstance(semester, int) or isinstance(semester, bool) or semester < 1:
            return JsonResponse(
                {'error': 'Semester must be a positive integer'},
                status=400
            )

        if Student.objects.filter(student_id=student_id).exists():
            return JsonResponse(
                {'error': 'This student ID already exists'},
                status=400
            )

        if status not in ['active', 'inactive']:
            return JsonResponse(
                {'error': 'Invalid student status'},
                status=400
            )

        student = Student.objects.create(
            name=name,
            student_id=student_id,
            department=department,
            semester=semester,
            status=status
        )

        return JsonResponse({
            'message': 'Student created successfully',
            'student_id': student.student_id
        }, status=201)

    except (json.JSONDecodeError, ValueError, TypeError):
        return JsonResponse(
            {'error': 'Invalid input data'},
            status=400
        )


def test_create_student(request):
    return HttpResponse("""
        <h2>Create Student</h2>

        <form id="student-form">
            <input name="name" placeholder="Name" required><br>
            <input name="student_id" placeholder="Student ID" required><br>
            <input name="department" placeholder="Department" required><br>
            <input name="semester" type="number" min="1" placeholder="Semester" required><br>

    <select name="status" required>
    <option value="active">Active</option>
    <option value="inactive">Inactive</option>
</select><br>

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
@login_required_api
def update_student(request, student_id):
    if request.method != 'PUT':
        return JsonResponse(
            {'error': 'Only PUT method is allowed'},
            status=405
        )

    student = get_object_or_404(Student, student_id=student_id)

    try:
        data = json.loads(request.body)
        name = data.get('name')
        department = data.get('department')
        semester = data.get('semester')
        status = data.get('status')

        if name is not None:
            student.name = name
        if department is not None:
            student.department = department
        if semester is not None:
            if not isinstance(semester, int) or isinstance(semester, bool) or semester < 1:
                return JsonResponse({'error': 'Semester must be a positive integer'}, status=400)
            student.semester = semester
        if status is not None:
            if status not in dict(Student.STATUS_CHOICES):
                return JsonResponse({'error': 'Invalid student status'}, status=400)
            student.status = status

        student.save()
        return JsonResponse({
            'message': 'Student updated successfully',
            'student_id': student.student_id,
        })
    except (json.JSONDecodeError, TypeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@csrf_exempt
@login_required_api
def delete_student(request, student_id):
    if request.method != 'DELETE':
        return JsonResponse(
            {'error': 'Only DELETE method is allowed'},
            status=405
        )

    student = get_object_or_404(Student, student_id=student_id)
    student.delete()

    return JsonResponse({
        'message': 'Student deleted successfully',
        'student_id': student_id,
    })
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

@login_required_api
def student_courses(request, student_id):

    student = get_object_or_404(Student, student_id=student_id)

    # Check user role
    profile = get_object_or_404(UserProfile, user=request.user)

    # Student can access only their own courses
    if profile.role == "student":
        if profile.student_id != student.id:
            return JsonResponse(
                {"error": "You are not allowed to access this student's courses"},
                status=403
            )

    # Only Admin and Student can access this API
    elif profile.role != "admin":
        return JsonResponse(
            {"error": "Permission denied"},
            status=403
        )

    enrollments = Enrollment.objects.filter(
        student=student
    ).select_related("course")

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

        username = data.get("username")
        password = data.get("password")
        role = data.get("role")
        student_id = data.get("student_id")

        if not username or not password or not role:
            return JsonResponse(
                {"error": "All required fields must be provided"},
                status=400
            )

        if role not in ["student", "teacher"]:
            return JsonResponse(
                {"error": "Invalid role"},
                status=400
            )

        if User.objects.filter(username=username).exists():
            return JsonResponse(
                {"error": "Username already exists"},
                status=400
            )

        student = None

        if role == "student":
            try:
                student = Student.objects.get(student_id=student_id)
            except (TypeError, ValueError):
                return JsonResponse({"error": "Valid Student ID is required"}, status=400)
            except Student.DoesNotExist:
                return JsonResponse({"error": "Student ID not found"}, status=404)

            if UserProfile.objects.filter(student=student).exists():
                return JsonResponse(
                    {"error": "This Student ID is already linked"},
                    status=400
                )

        user = User.objects.create_user(
            username=username,
            password=password
        )

        UserProfile.objects.create(
            user=user,
            role=role,
            student=student
        )

        return JsonResponse({
            "success": True,
            "message": "Registration successful",
            "username": username,
            "role": role
        })

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=400
        )

def test_register(request):
    return HttpResponse("""
        <h2>Register Test</h2>

        <input id="username" placeholder="Username"><br><br>

        <input id="password" type="password" placeholder="Password"><br><br>

        <select id="role">
            <option value="student">Student</option>
            <option value="teacher">Teacher</option>
        </select><br><br>

        <input id="student_id" type="number" placeholder="Student ID"><br><br>

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
                    role: document.getElementById('role').value,
                    student_id: document.getElementById('student_id').value
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
    try:
        role = user.userprofile.role
    except UserProfile.DoesNotExist:
        return JsonResponse(
            {"error": "User profile not found"},
            status=403
        )

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