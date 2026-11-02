from django.contrib import admin
from .models import Student
from .models import Student, Course, ClassSchedule, Enrollment

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'student_id', 'department')


admin.site.register(Course)
admin.site.register(ClassSchedule)
admin.site.register(Enrollment)
