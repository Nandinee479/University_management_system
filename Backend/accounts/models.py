from django.db import models
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