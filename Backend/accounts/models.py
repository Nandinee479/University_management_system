from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    name = models.CharField(max_length=100)
    student_id = models.IntegerField(unique=True)
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Course(models.Model):
    course_code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=100)
    credits = models.PositiveIntegerField()
    semester = models.PositiveIntegerField()
    department = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    instructor_name = models.CharField(max_length=100)
    instructor_email = models.EmailField(blank=True)

    def __str__(self):
        return f"{self.course_code} - {self.title}"
class ClassSchedule(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="schedules"
    )
    day = models.CharField(max_length=20)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.course.course_code} - {self.day}"

class Enrollment(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    class Meta:
        unique_together = ("student", "course")

    def __str__(self):
        return f"{self.student.student_id} - {self.course.course_code}"

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("teacher", "Teacher"),
        ("student", "Student"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"