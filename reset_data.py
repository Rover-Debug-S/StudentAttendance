#!/usr/bin/env python3
"""
Reset database and create fresh test data for Student Attendance System
"""
from app import app, db
from models import Student, Section, User, Attendance
from werkzeug.security import generate_password_hash
from datetime import datetime

def reset_database():
    print("🔄 Resetting Student Attendance System Database...\n")

    with app.app_context():
        # Drop all tables and recreate
        print("1. Dropping all tables...")
        db.drop_all()

        print("2. Creating all tables...")
        db.create_all()

        print("3. Creating default sections...")
        # Create sections
        sections_data = [
            ('A', 1),
            ('B', 1),
            ('C', 2),
            ('D', 2),
        ]
        sections = []
        for name, grade_level in sections_data:
            section = Section(name=name, grade_level=grade_level)
            db.session.add(section)
            sections.append(section)
        db.session.commit()
        print(f"   ✓ Created {len(sections)} sections")

        print("4. Creating default students...")
        # Create students
        students_data = [
            ('John Doe', 1, 1),
            ('Jane Smith', 1, 1),
            ('Bob Johnson', 1, 2),
            ('Alice Brown', 1, 2),
            ('Charlie Wilson', 2, 3),
            ('Diana Davis', 2, 3),
            ('Edward Miller', 2, 4),
            ('Fiona Garcia', 2, 4),
        ]
        students = []
        for name, grade_level, section_id in students_data:
            student = Student(name=name, grade_level=grade_level, section_id=section_id)
            db.session.add(student)
            students.append(student)
        db.session.commit()
        print(f"   ✓ Created {len(students)} students")

        print("5. Creating parent accounts...")
        # Create parents with mobile numbers
        parents_data = [
            ('parent1', 'parent123', 1, '09123456789'),
            ('parent2', 'parent123', 2, '09123456790'),
            ('parent3', 'parent123', 3, '09123456791'),
            ('parent4', 'parent123', 4, '09123456792'),
            ('parent5', 'parent123', 5, '09123456793'),
            ('parent6', 'parent123', 6, '09123456794'),
            ('parent7', 'parent123', 7, '09123456795'),
            ('parent8', 'parent123', 8, '09123456796'),
        ]
        parents = []
        for username, password, student_id, mobile in parents_data:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            parent = User(username=username, password=hashed_password, role='parent', student_id=student_id, mobile=mobile)
            db.session.add(parent)
            parents.append(parent)
        db.session.commit()
        print(f"   ✓ Created {len(parents)} parent accounts")

        print("6. Creating host account...")
        # Create host
        hashed_password = generate_password_hash('host123', method='pbkdf2:sha256')
        host = User(username='host', password=hashed_password, role='host')
        db.session.add(host)
        db.session.commit()
        print("   ✓ Created host account")

        print("7. Creating sample attendance data...")
        # Create some sample attendance records
        today = datetime.now().date()
        yesterday = today.replace(day=today.day - 1) if today.day > 1 else today

        # Today's attendance
        for i, student in enumerate(students):
            status = 'present' if i % 3 != 0 else 'absent'  # Mix of present and absent
            attendance = Attendance(student_id=student.id, date=today, status=status)
            db.session.add(attendance)

        # Yesterday's attendance
        for i, student in enumerate(students):
            status = 'present' if i % 2 == 0 else 'absent'  # Different pattern
            attendance = Attendance(student_id=student.id, date=yesterday, status=status)
            db.session.add(attendance)

        db.session.commit()
        print("   ✓ Created sample attendance records")

        print("\n🎉 Database reset complete!")
        print("\n📊 Summary:")
        print(f"   Sections: {len(sections)}")
        print(f"   Students: {len(students)}")
        print(f"   Parents: {len(parents)}")
        print(f"   Attendance Records: {len(Attendance.query.all())}")

        print("\n🔐 Login Credentials:")
        print("   Host: host / host123")
        print("   Parents: parent1 to parent8 / parent123")
        print("   (Each parent can see their child's attendance)")

        print("\n📱 SMS Configuration:")
        print("   Email: zidious57@gmail.com")
        print("   Gateway: smart.com.ph")
        print("   SMS will be sent when marking attendance")

        print("\n🚀 Ready to use!")
        print("   Run: python app.py")
        print("   Open: http://localhost:5000")

if __name__ == '__main__':
    reset_database()
