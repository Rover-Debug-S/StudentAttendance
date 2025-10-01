import os
from db import db
from app import app
from models import User, Student, Section, Attendance

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'attendance.db'))
print(f"Database path: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

with app.app_context():
    print("\n=== USERS ===")
    users = User.query.all()
    print(f"Number of users: {len(users)}")
    for user in users:
        print(f"User: {user.username}, Role: {user.role}, Student ID: {user.student_id}, Mobile: {user.mobile}")

    print("\n=== SECTIONS ===")
    sections = Section.query.all()
    print(f"Number of sections: {len(sections)}")
    for section in sections:
        print(f"Section: {section.name}, Grade: {section.grade_level}")

    print("\n=== STUDENTS ===")
    students = Student.query.all()
    print(f"Number of students: {len(students)}")
    for student in students:
        print(f"Student: {student.name}, Grade: {student.grade_level}, Section: {student.section.name if student.section else 'No Section'}")
        print(f"  Parents: {[p.username for p in student.parents]}")

    print("\n=== ATTENDANCE RECORDS ===")
    attendances = Attendance.query.all()
    print(f"Number of attendance records: {len(attendances)}")
    for attendance in attendances:
        print(f"Attendance: {attendance.student.name} - {attendance.date} - {attendance.status}")
