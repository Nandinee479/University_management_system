import json

from django.contrib.auth.models import User
from django.test import TestCase

from .models import Student, UserProfile


class StudentApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="test-password")
        UserProfile.objects.create(user=self.user, role="admin")
        self.client.login(username="admin", password="test-password")

    def test_create_and_filter_student(self):
        response = self.client.post(
            "/student/create/",
            data=json.dumps({
                "name": "Nadia",
                "student_id": "S-100",
                "department": "CSE",
                "semester": 3,
                "status": "active",
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)

        response = self.client.get("/student/", {"search": "S-100"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["student_id"], "S-100")

    def test_create_rejects_invalid_semester(self):
        response = self.client.post(
            "/student/create/",
            data=json.dumps({
                "name": "Nadia",
                "student_id": "S-101",
                "department": "CSE",
                "semester": 0,
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_update_and_delete_student(self):
        student = Student.objects.create(
            name="Old Name",
            student_id="S-102",
            department="CSE",
            semester=1,
        )

        response = self.client.put(
            f"/student/{student.student_id}/update/",
            data=json.dumps({
                "name": "New Name",
                "department": "EEE",
                "semester": 2,
                "status": "inactive",
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        student.refresh_from_db()
        self.assertEqual(student.name, "New Name")
        self.assertEqual(student.semester, 2)
        self.assertEqual(student.status, "inactive")

        response = self.client.delete(f"/student/{student.student_id}/delete/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Student.objects.filter(student_id="S-102").exists())


class RegistrationApiTests(TestCase):
    def test_register_student_by_student_id(self):
        Student.objects.create(
            name="Student",
            student_id="S-200",
            department="CSE",
        )

        response = self.client.post(
            "/register/",
            data=json.dumps({
                "username": "student-user",
                "password": "test-password",
                "role": "student",
                "student_id": "S-200",
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username="student-user").exists())
