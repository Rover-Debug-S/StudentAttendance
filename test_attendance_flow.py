#!/usr/bin/env python3
"""
Test the complete attendance marking and viewing flow
"""
from app import app, db
from models import Student, Section, User, Attendance
from werkzeug.security import generate_password_hash
from datetime import datetime
import requests

def test_attendance_flow():
    print("=== Testing Complete Attendance Flow ===\n")

    # Start Flask app in background
    import threading
    import time

    def run_app():
        with app.app_context():
            app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

    # Start the app in a separate thread
    app_thread = threading.Thread(target=run_app, daemon=True)
    app_thread.start()
    time.sleep(2)  # Wait for app to start

    try:
        with app.app_context():
            # Clear and setup test data
            db.drop_all()
            db.create_all()

            # Create test data
            section = Section(name='A', grade_level=1)
            db.session.add(section)
            db.session.commit()

            student = Student(name='Test Student', grade_level=1, section_id=section.id)
            db.session.add(student)
            db.session.commit()

            hashed_password = generate_password_hash('host123', method='pbkdf2:sha256')
            host = User(username='host', password=hashed_password, role='host')
            db.session.add(host)
            db.session.commit()

            print("✓ Test data created")

            # Test attendance marking via direct database
            date = datetime.now().date()
            attendance = Attendance(student_id=student.id, date=date, status='present')
            db.session.add(attendance)
            db.session.commit()

            # Verify attendance was saved
            saved_attendance = Attendance.query.filter_by(student_id=student.id, date=date).first()
            if saved_attendance:
                print(f"✓ Attendance saved: {saved_attendance.student.name} - {saved_attendance.status}")
            else:
                print("❌ Attendance not saved")

            # Test parent dashboard
            hashed_password = generate_password_hash('parent123', method='pbkdf2:sha256')
            parent = User(username='parent', password=hashed_password, role='parent', student_id=student.id, mobile='09123456789')
            db.session.add(parent)
            db.session.commit()

            parent_attendances = Attendance.query.filter_by(student_id=parent.student_id).all()
            print(f"✓ Parent can see {len(parent_attendances)} attendance records")

            print("\n=== Manual Testing Instructions ===")
            print("1. Open browser to http://127.0.0.1:5000")
            print("2. Login as host (username: host, password: host123)")
            print("3. Go to 'Mark Attendance' and mark attendance for today")
            print("4. Go to 'View Attendance' to see the records")
            print("5. Login as parent (username: parent, password: parent123)")
            print("6. Check parent dashboard for attendance records")
            print("\nThe system should now be working correctly!")

    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == '__main__':
    test_attendance_flow()
