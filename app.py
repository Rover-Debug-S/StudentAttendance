from flask import Flask, render_template, request, redirect, url_for, Response, flash
from flask_login import LoginManager, login_required, logout_user, current_user
from datetime import datetime
from db import db
import csv
import io
from werkzeug.security import generate_password_hash, check_password_hash
from twilio.rest import Client
import os
from sqlalchemy.orm import joinedload
import smtplib
from email.mime.text import MIMEText

# Email and SMS configuration
EMAIL_USER = 'jafflusica48@gmail.com'
EMAIL_PASS = 'wnaw mwrw bqxp sqcj'
SMS_GATEWAY = 'smart.com.ph'

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

# Create database tables and default data when app starts
with app.app_context():
    db.create_all()
    create_default_data()
    create_default_host()

@app.route('/')
def index():
    return redirect(url_for('login'))

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

@app.route('/parent_register', methods=['GET', 'POST'])
def parent_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        student_id = request.form['student_id']
        mobile = request.form['mobile']
        email = request.form['email']

        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('parent_register'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('parent_register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_parent = User(username=username, password=hashed_password, role='parent', student_id=student_id, mobile=mobile, email=email)
        db.session.add(new_parent)
        db.session.commit()

        flash('Registration successful! Please login.')
        return redirect(url_for('login'))

    return render_template('parent_register.html')

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
    student = Student.query.get(current_user.student_id)
    attendances = Attendance.query.filter_by(student_id=current_user.student_id).all()
    return render_template('parent_dashboard.html', student=student, attendances=attendances)

@app.route('/api/search_students')
def api_search_students():
    query = request.args.get('q', '')
    if len(query) < 2:
        return {'students': []}
    students = Student.query.filter(Student.name.ilike(f'%{query}%')).all()
    results = []
    for student in students:
        section = Section.query.get(student.section_id)
        results.append({
            'id': student.id,
            'name': student.name,
            'grade_level': student.grade_level,
            'section_name': section.name
        })
    return {'students': results}

@app.route('/api/parent_attendance/<int:user_id>')
def api_parent_attendance(user_id):
    user = User.query.get(user_id)
    if not user or user.role != 'parent':
        return {'error': 'User not found'}, 404
    attendances = Attendance.query.filter_by(student_id=user.student_id).all()
    results = []
    for attendance in attendances:
        results.append({
            'date': attendance.date.strftime('%Y-%m-%d'),
            'status': attendance.status
        })
    return results, 200

def send_notification(parent, message):
    """Send notification to parent via SMS and email if available"""
    if parent.mobile:
        send_sms_to_mobile(parent.mobile, message)
    if parent.email:
        send_email_to_parent(parent.email, message)

def send_sms_to_mobile(phone_number, message):
    """Send SMS to mobile number"""
    try:
        # Strip leading 0 from phone number for SMS gateway
        phone_number = phone_number.lstrip('0')

        # Convert phone to email format (e.g., 9948154088@smart.com.ph)
        sms_email = f"{phone_number}@{SMS_GATEWAY}"

        msg = MIMEText(message)
        msg['Subject'] = 'Student Attendance Notification'
        msg['From'] = EMAIL_USER
        msg['To'] = sms_email

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, sms_email, msg.as_string())
        server.quit()

        print(f"✅ SMS sent successfully to {phone_number}")
        return True
    except Exception as e:
        print(f"❌ SMS failed: {e}")
        return False

def send_email_to_parent(email, message):
    """Send email to parent"""
    try:
        msg = MIMEText(message)
        msg['Subject'] = 'Student Attendance Notification'
        msg['From'] = EMAIL_USER
        msg['To'] = email

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, email, msg.as_string())
        server.quit()

        print(f"✅ Email sent successfully to {email}")
        return True
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False

# Attendance marking routes with notifications
@app.route('/mark_attendance/<int:student_id>', methods=['POST'])
@login_required
def mark_attendance(student_id):
    if current_user.role != 'host':
        return redirect(url_for('login'))
    status = request.form['status']
    date = datetime.now().date()
    attendance = Attendance.query.filter_by(student_id=student_id, date=date).first()
    if attendance:
        attendance.status = status
    else:
        attendance = Attendance(student_id=student_id, date=date, status=status)
        db.session.add(attendance)
    db.session.commit()

    student = Student.query.get(student_id)
    parents = User.query.filter_by(student_id=student_id, role='parent').all()
    for parent in parents:
        message = f"{student.name} is {status} on {date}"
        send_notification(parent, message)
    return redirect(url_for('host_dashboard'))

@app.route('/upload_attendance', methods=['POST'])
@login_required
def upload_attendance():
    if current_user.role != 'host':
        return redirect(url_for('login'))
    file = request.files['file']
    if file:
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)
        next(csv_input)  # Skip header
        for row in csv_input:
            student_name, status, date_str = row
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            student = Student.query.filter_by(name=student_name).first()
            if student:
                attendance = Attendance.query.filter_by(student_id=student.id, date=date).first()
                if attendance:
                    attendance.status = status
                else:
                    attendance = Attendance(student_id=student.id, date=date, status=status)
                    db.session.add(attendance)
                db.session.commit()

                parents = User.query.filter_by(student_id=student.id, role='parent').all()
                for parent in parents:
                    message = f"{student.name} is {status} on {date}"
                    send_notification(parent, message)
    return redirect(url_for('host_dashboard'))

def create_default_host():
    host = User.query.filter_by(username='host').first()
    if not host:
        hashed_password = generate_password_hash('host123', method='pbkdf2:sha256')
        host = User(username='host', password=hashed_password, role='host')
        db.session.add(host)
        db.session.commit()

def create_default_data():
    """Create default students, sections, and parents for testing"""
    # Create sections
    if Section.query.count() == 0:
        section1 = Section(name='A', grade_level=1)
        section2 = Section(name='B', grade_level=1)
        db.session.add(section1)
        db.session.add(section2)
        db.session.commit()

    # Create students
    if Student.query.count() == 0:
        students_data = [
            ('John Doe', 1, 1),
            ('Jane Smith', 1, 1),
            ('Bob Johnson', 1, 2),
            ('Alice Brown', 1, 2)
        ]
        for name, grade, section_id in students_data:
            student = Student(name=name, grade_level=grade, section_id=section_id)
            db.session.add(student)
        db.session.commit()

    # Create parents
    if User.query.filter_by(role='parent').count() == 0:
        parents_data = [
            ('parent1', 'parent123', 1, '09123456789', 'parent1@example.com'),
            ('parent2', 'parent123', 2, '09123456790', 'parent2@example.com'),
            ('parent3', 'parent123', 3, '09123456791', 'parent3@example.com'),
            ('parent4', 'parent123', 4, '09123456792', 'parent4@example.com')
        ]
        for username, password, student_id, mobile, email in parents_data:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            parent = User(username=username, password=hashed_password, role='parent', student_id=student_id, mobile=mobile, email=email)
            db.session.add(parent)
        db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
