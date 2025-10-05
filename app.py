from flask import Flask, render_template, request, redirect, url_for, Response, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from datetime import datetime
from db import db
import csv
import io
from werkzeug.security import generate_password_hash, check_password_hash
from twilio.rest import Client
import os
from sqlalchemy.orm import joinedload

app = Flask(__name__)

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'attendance.db'))
print(f"Using database file at: {db_path}")

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"Using database file at: {db_path}")

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from models import Student, Attendance, User, Section

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"Login attempt: username={username}")
        user = User.query.filter_by(username=username).first()
        print(f"User found: {user is not None}")
        if user:
            print(f"User role: {user.role}")
            print(f"Password check: {check_password_hash(user.password, password)}")
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == 'host':
                return redirect(url_for('host_dashboard'))
            elif user.role == 'parent':
                return redirect(url_for('parent_dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/host_dashboard')
@login_required
def host_dashboard():
    if current_user.role != 'host':
        return redirect(url_for('login'))
    students = Student.query.all()
    sections = Section.query.all()
    return render_template('host_dashboard.html', students=students, sections=sections)

@app.route('/parent_dashboard')
@login_required
def parent_dashboard():
    if current_user.role != 'parent':
        return redirect(url_for('login'))
    attendances = Attendance.query.filter_by(student_id=current_user.student_id).all()
    return render_template('parent_dashboard.html', attendances=attendances)

# SMS Configuration - FREE & EASY Alternatives (No Age Restrictions!)
SMS_METHOD = 'email'  # Options: console, email, file

# For console mode (FREE - just prints to terminal)
# For email mode (FREE - uses your email)
EMAIL_USER = 'zidious57@gmail.com'
EMAIL_PASS = 'wnaw mwrw bqxp sqcj'
SMS_GATEWAY = 'smart.com.ph'

def send_notification(mobile, email, message):
    """Send notification via SMS and/or email"""
    success = False
    
    if mobile and SMS_METHOD == 'email' and EMAIL_USER and EMAIL_PASS:
        # Send SMS via email gateway
        try:
            import smtplib
            from email.mime.text import MIMEText

            # Strip leading 0 from phone number for SMS gateway
            phone_number = mobile.lstrip('0')

            # Convert phone to email format (e.g., 1234567890@smart.com.ph)
            sms_email = f"{phone_number}@{SMS_GATEWAY}"

            msg = MIMEText(message)
            msg['Subject'] = 'Attendance Update'
            msg['From'] = EMAIL_USER
            msg['To'] = sms_email

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, sms_email, msg.as_string())
            server.quit()

            print(f"✅ SMS sent to {mobile} via email to {sms_email}")
            success = True
        except Exception as e:
            print(f"❌ SMS failed: {e}")

    if email and EMAIL_USER and EMAIL_PASS:
        # Send direct email notification
        try:
            import smtplib
            from email.mime.text import MIMEText

            msg = MIMEText(f"Attendance Update: {message}")
            msg['Subject'] = 'Attendance Update'
            msg['From'] = EMAIL_USER
            msg['To'] = email

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, email, msg.as_string())
            server.quit()

            print(f"✅ Email sent to {email}")
            success = True
        except Exception as e:
            print(f"❌ Email failed: {e}")

    if SMS_METHOD == 'console':
        # Console logging for both
        if mobile:
            print(f"📱 SMS to {mobile}: {message}")
        if email:
            print(f"📧 Email to {email}: {message}")
        success = True

    elif SMS_METHOD == 'file':
        # File logging
        with open('notification_log.txt', 'a') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if mobile:
                f.write(f"{timestamp}: SMS to {mobile}: {message}\n")
            if email:
                f.write(f"{timestamp}: Email to {email}: {message}\n")
        print(f"📄 Notification logged to file")
        success = True

    return success

# Initialize SMS system
print(f"📡 SMS System initialized with method: {SMS_METHOD}")

@app.route('/')
@login_required
def index():
    if current_user.role == 'host':
        return redirect(url_for('host_dashboard'))
    elif current_user.role == 'parent':
        return redirect(url_for('parent_dashboard'))
    return redirect(url_for('login'))

@app.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    if current_user.role != 'host':
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        grade_level = int(request.form['grade_level'])
        section_id = int(request.form['section_id'])
        new_student = Student(name=name, grade_level=grade_level, section_id=section_id)
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for('host_dashboard'))
    sections = Section.query.all()
    return render_template('add_student.html', sections=sections)

@app.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    if current_user.role != 'host':
        return redirect(url_for('login'))
    student = Student.query.get_or_404(student_id)
    if request.method == 'POST':
        student.name = request.form['name']
        student.grade_level = int(request.form['grade_level'])
        student.section_id = int(request.form['section_id'])
        db.session.commit()
        return redirect(url_for('host_dashboard'))
    sections = Section.query.all()
    return render_template('edit_student.html', student=student, sections=sections)

@app.route('/delete_student/<int:student_id>', methods=['POST', 'GET'])
@login_required
def delete_student(student_id):
    if current_user.role != 'host':
        return redirect(url_for('login'))
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('host_dashboard'))

@app.route('/add_section', methods=['GET', 'POST'])
@login_required
def add_section():
    if current_user.role != 'host':
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        grade_level = int(request.form['grade_level'])
        new_section = Section(name=name, grade_level=grade_level)
        db.session.add(new_section)
        db.session.commit()
        return redirect(url_for('host_dashboard'))
    return render_template('add_section.html')

@app.route('/edit_section/<int:section_id>', methods=['GET', 'POST'])
@login_required
def edit_section(section_id):
    if current_user.role != 'host':
        return redirect(url_for('login'))
    section = Section.query.get_or_404(section_id)
    if request.method == 'POST':
        section.name = request.form['name']
        section.grade_level = int(request.form['grade_level'])
        db.session.commit()
        return redirect(url_for('host_dashboard'))
    return render_template('edit_section.html', section=section)

@app.route('/delete_section/<int:section_id>', methods=['POST', 'GET'])
@login_required
def delete_section(section_id):
    if current_user.role != 'host':
        return redirect(url_for('login'))
    section = Section.query.get_or_404(section_id)
    db.session.delete(section)
    db.session.commit()
    return redirect(url_for('host_dashboard'))

import pytesseract
from PIL import Image
import tempfile

# Configure Tesseract path for Windows
def configure_tesseract():
    """Configure Tesseract OCR path for Windows"""
    try:
        # Try common installation paths
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            r'C:\Users\Windows 10\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
        ]

        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                print(f"✅ Tesseract found at: {path}")
                return True

        # If not found in common paths, try to use from PATH
        try:
            pytesseract.get_tesseract_version()
            print("✅ Tesseract found in PATH")
            return True
        except Exception:
            print("❌ Tesseract not found. Please install Tesseract OCR.")
            print("📖 See TESSERACT_INSTALL_GUIDE.md for installation instructions.")
            return False

    except Exception as e:
        print(f"❌ Tesseract configuration error: {e}")
        return False

# Initialize Tesseract
TESSERACT_AVAILABLE = configure_tesseract()

@app.route('/mark_attendance', methods=['GET', 'POST'])
@login_required
def mark_attendance():
    if current_user.role != 'host':
        return redirect(url_for('login'))
    if request.method == 'POST':
        date_str = request.form['date']
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        students = Student.query.options(joinedload(Student.parents)).all()
        for student in students:
            status = request.form.get(f'status_{student.id}', 'absent')
            # Check if attendance record already exists for this student and date
            existing_attendance = Attendance.query.filter_by(student_id=student.id, date=date).first()
            if existing_attendance:
                existing_attendance.status = status
            else:
                attendance = Attendance(student_id=student.id, date=date, status=status)
                db.session.add(attendance)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving attendance: {str(e)}')
            return redirect(url_for('host_dashboard'))
        # Send SMS notification to parents using the configured method
        for student in students:
            for parent in student.parents:
                if parent.role == 'parent' and (parent.mobile or parent.email):
                    status = request.form.get(f'status_{student.id}', 'absent')
                    message = f"{student.name} is {status} on {date}"
                    send_notification(parent.mobile, parent.email, message)
        return redirect(url_for('host_dashboard'))
    students = Student.query.all()
    return render_template('mark_attendance.html', students=students)

@app.route('/upload_attendance', methods=['GET', 'POST'])
@login_required
def upload_attendance():
    if current_user.role != 'host':
        return redirect(url_for('login'))

    if not TESSERACT_AVAILABLE:
        flash('Tesseract OCR is not installed. Please install it to use image-based attendance marking. See TESSERACT_INSTALL_GUIDE.md for instructions.')
        return redirect(url_for('host_dashboard'))

    if request.method == 'POST':
        date_str = request.form['date']
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        if 'attendance_image' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['attendance_image']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            try:
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    file.save(tmp.name)

                    # Enhanced OCR processing
                    image = Image.open(tmp.name)

                    # Preprocessing for better OCR accuracy
                    import cv2
                    import numpy as np

                    # Convert PIL to OpenCV format
                    opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

                    # Convert to grayscale
                    gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)

                    # Apply threshold to get better contrast
                    _, threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

                    # Perform OCR with better configuration
                    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789. '
                    text = pytesseract.image_to_string(threshold, config=custom_config)

                # Enhanced name extraction and cleaning
                recognized_names = set()
                raw_text = text.lower()

                # Get all students for comparison
                all_students = Student.query.all()
                student_names = {student.name.lower(): student for student in all_students}

                # Extract potential names using multiple methods
                lines = text.split('\n')

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    # Clean the line
                    cleaned_line = ''.join(c for c in line if c.isalnum() or c.isspace()).strip()

                    # Check if this line contains any student names
                    for student_name, student in student_names.items():
                        # Exact match
                        if student_name == cleaned_line.lower():
                            recognized_names.add(student_name)
                        # Partial match (student name within the line)
                        elif student_name in cleaned_line.lower():
                            recognized_names.add(student_name)
                        # Fuzzy match for common OCR errors
                        elif len(student_name) > 3:
                            # Check if most characters match (allowing for OCR errors)
                            student_chars = set(student_name.replace(' ', ''))
                            line_chars = set(cleaned_line.lower().replace(' ', ''))

                            if len(student_chars.intersection(line_chars)) / len(student_chars) > 0.8:
                                recognized_names.add(student_name)

                # Also check the entire text for names that might span multiple lines
                for student_name in student_names.keys():
                    if student_name in raw_text:
                        recognized_names.add(student_name)

                # Get matched students only
                matched_students = []
                detected_student_ids = []

                for student in all_students:
                    if student.name.lower() in recognized_names:
                        matched_students.append(student)
                        detected_student_ids.append(student.id)

                # Always show all students, but mark detected as present
                detected_student_ids = [s.id for s in matched_students]

                # Render review page with all students
                return render_template('review_attendance_improved.html',
                                     date=date,
                                     students=all_students,
                                     detected_student_ids=detected_student_ids,
                                     detected_names=recognized_names,
                                     all_students_count=len(all_students),
                                     matched_students_count=len(matched_students))

            except Exception as e:
                flash(f'Error processing image: {str(e)}')
                return redirect(request.url)

    return render_template('upload_attendance.html')
    
@app.route('/review_attendance', methods=['POST'])
@login_required
def review_attendance():
    if current_user.role != 'host':
        return redirect(url_for('login'))
    date_str = request.form.get('date')
    if not date_str:
        flash('Date is required for attendance review.')
        return redirect(url_for('host_dashboard'))
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format.')
        return redirect(url_for('host_dashboard'))
    students = Student.query.options(joinedload(Student.parents)).all()
    for student in students:
        status = request.form.get(f'status_{student.id}', 'absent')
        # Check if attendance record already exists for this student and date
        existing_attendance = Attendance.query.filter_by(student_id=student.id, date=date).first()
        if existing_attendance:
            existing_attendance.status = status
        else:
            attendance = Attendance(student_id=student.id, date=date, status=status)
            db.session.add(attendance)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Error saving attendance: {str(e)}')
        return redirect(url_for('host_dashboard'))
    # Send SMS notification to parents using the configured method
    for student in students:
        for parent in student.parents:
            if parent.role == 'parent' and (parent.mobile or parent.email):
                status = request.form.get(f'status_{student.id}', 'absent')
                message = f"{student.name} is {status} on {date}"
                send_notification(parent.mobile, parent.email, message)
    return redirect(url_for('host_dashboard'))

@app.route('/view_attendance')
@login_required
def view_attendance():
    if current_user.role != 'host':
        return redirect(url_for('login'))
    query = Attendance.query.options(joinedload(Attendance.student))
    if request.args.get('student'):
        query = query.filter_by(student_id=request.args.get('student'))
    if request.args.get('grade'):
        grade_students = Student.query.filter_by(grade_level=int(request.args.get('grade'))).all()
        grade_student_ids = [s.id for s in grade_students]
        query = query.filter(Attendance.student_id.in_(grade_student_ids))
    if request.args.get('section'):
        section_students = Student.query.filter_by(section_id=int(request.args.get('section'))).all()
        section_student_ids = [s.id for s in section_students]
        query = query.filter(Attendance.student_id.in_(section_student_ids))
    if request.args.get('date'):
        query = query.filter_by(date=request.args.get('date
