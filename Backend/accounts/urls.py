from django.urls import path
from . import views

urlpatterns = [
    path('', views.hello, name='hello'),
    path('student/', views.student_info, name='student_info'),
    path('student/create/', views.create_student, name='create_student'),
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),
    path('test-create/', views.test_create_student, name='test_create_student'),
    path('student/<int:student_id>/update/', views.update_student, name='update_student'),
    path('test-delete/', views.test_delete_student, name='test_delete_student'),
    path('student/<int:student_id>/delete/', views.delete_student, name='delete_student'),
    path('student/<int:student_id>/courses/', views.student_courses, name='student_courses'),
]