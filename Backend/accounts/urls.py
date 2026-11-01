from django.urls import path
from . import views
urlpatterns = [
    path('', views.hello, name='hello'),
    path('student/', views.student_info, name='student_info'),
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),
]
