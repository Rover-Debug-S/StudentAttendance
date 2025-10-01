#!/usr/bin/env python3
"""
Test script to verify the attendance system functionality
"""
from app import app, db
from models import Student, Section, User, Attendance
from werkzeug.security import generate_password_hash
from datetime import datetime

def test_system():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        print("=== Testing Student Attendance System ===\n")

        # Create sections
        print("1. Creating sections...")
        section1 = Section(name='A', grade_level=1)
        section2 = Section(name='B', grade_level=1)
        db.session.add(section1)
        db.session.add(section2)
        db.session.commit()
        print(f"   ✓ Created sections: {section1.name}, {section2.name}")

        # Create students
        print("\n2. Creating students...")
        students_data = [
            ('John Doe', 1, 1),
            ('Jane Smith', 1, 1),
            ('Bob Johnson', 1, 2),
            ('Alice Brown', 1, 2)
        ]
        students = []
        for name, grade, section_id in students_data:
            student = Student(name=name, grade_level=grade, section_id=section_id)
            db.session.add(student)
            students.append(student)
        db.session.commit()
        print(f"   ✓ Created {len(students)} students")

        # Create parents
        print("\n3. Creating parents...")
        parents_data = [
            ('parent1', 'parent123', 1, '09123456789'),
            ('parent2', 'parent123', 2, '09123456790'),
            ('parent3', 'parent123', 3, '09123456791'),
            ('parent4', 'parent123', 4, '09123456792')
        ]
        parents = []
        for username, password, student_id, mobile in parents_data:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            parent = User(username=username, password=hashed_password, role='parent', student_id=student_id, mobile=mobile)
            db.session.add(parent)
            parents.append(parent)
        db.session.commit()
        print(f"   ✓ Created {len(parents)} parents")

        # Create host
        print("\n4. Creating host...")
        hashed_password = generate_password_hash('host123', method='pbkdf2:sha256')
        host = User(username='host', password=hashed_password, role='host')
        db.session.add(host)
        db.session.commit()
        print("   ✓ Created host user")

        # Test attendance marking
        print("\n5. Testing attendance marking...")
        date = datetime.now().date()
        attendance_records = []
        for i, student in enumerate(students):
            status = 'present' if i % 2 == 0 else 'absent'
            attendance = Attendance(student_id=student.id, date=date, status=status)
            db.session.add(attendance)
            attendance_records.append(attendance)
        db.session.commit()
        print(f"   ✓ Created {len(attendance_records)} attendance records")

        # Verify attendance records
        print("\n6. Verifying attendance records...")
        all_attendances = Attendance.query.all()
        print(f"   ✓ Found {len(all_attendances)} attendance records in database")

        for attendance in all_attendances:
            print(f"     - {attendance.student.name}: {attendance.status} on {attendance.date}")

        # Test parent dashboard
        print("\n7. Testing parent dashboard...")
        for parent in parents:
            parent_attendances = Attendance.query.filter_by(student_id=parent.student_id).all()
            print(f"   ✓ Parent {parent.username} can see {len(parent_attendances)} attendance records for {parent.student.name}")

        print("\n=== Test Complete ===")
        print("✅ All core functionality appears to be working!")
        print("\nNext steps:")
        print("1. Run the Flask app: python app.py")
        print("2. Login as host (username: host, password: host123)")
        print("3. Add more students and mark attendance")
        print("4. Login as parent (username: parent1, password: parent123)")
        print("5. Check parent dashboard for attendance records")

if __name__ == '__main__':
    test_system()
