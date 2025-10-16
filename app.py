from flask import Flask, render_template, request, redirect, url_for, Response, flash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_cors import CORS
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
EMAIL_USER = os.environ.get('EMAIL_USER', 'default@example.com')
EMAIL_PASS = os.environ.get('EMAIL_PASS', 'default_pass')
SMS_GATEWAY = 'smart.com.ph'

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

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

# Create database tables and default data when app starts
with app.app_context():
    try:
        db.create_all()
        create_default_data()
        create_default_host()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        print("This might be due to schema changes. Try deleting the attendance.db file and restarting.")

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

    students = Student.query.all()
    return render_template('parent_register.html', students=students)

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

@app.route('/update_contact', methods=['GET', 'POST'])
@login_required
def update_contact():
    if current_user.role != 'parent':
        return redirect(url_for('login'))
    if request.method == 'POST':
        mobile = request.form['mobile']
        email = request.form['email']
        current_user.mobile = mobile
        current_user.email = email
        db.session.commit()
        flash('Contact information updated successfully!')
        return redirect(url_for('parent_dashboard'))
    return render_template('update_contact.html', parent=current_user)

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


@app.route('/api/parent_login', methods=['POST'])
def api_parent_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username, role='parent').first()
    if user and check_password_hash(user.password, password):
        return jsonify({'parent_id': user.id}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/api/parent_register', methods=['POST'])
def api_parent_register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    mobile = data.get('mobile')
    email = data.get('email')
    student_id = data.get('student_id')
    
    if not all([username, password, mobile, email, student_id]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_parent = User(
        username=username, 
        password=hashed_password, 
        role='parent', 
        student_id=student_id, 
        mobile=mobile, 
        email=email
    )
    db.session.add(new_parent)
    db.session.commit()
    
    return jsonify({'message': 'Registration successful'}), 201


@app.route('/api/parent_dashboard/<int:parent_id>', methods=['GET'])
def api_parent_dashboard(parent_id):
    user = User.query.get(parent_id)
    if not user or user.role != 'parent':
        return jsonify({'error': 'User not found'}), 404
    
    student = Student.query.get(user.student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    return jsonify({
        'student_name': student.name,
        'mobile': user.mobile,
        'email': user.email
    }), 200


@app.route('/api/update_mobile/<int:parent_id>', methods=['POST'])
def api_update_mobile(parent_id):
    data = request.get_json()
    mobile = data.get('mobile')
    
    user = User.query.get(parent_id)
    if not user or user.role != 'parent':
        return jsonify({'error': 'User not found'}), 404
    
    user.mobile = mobile
    db.session.commit()
    
    return jsonify({'message': 'Mobile updated successfully'}), 200


@app.route('/api/parent_attendance/<int:parent_id>', methods=['GET'])
def api_parent_attendance(parent_id):
    user = User.query.get(parent_id)
    if not user or user.role != 'parent':
        return jsonify({'error': 'User not found'}), 404
    
    attendances = Attendance.query.filter_by(student_id=user.student_id).all()
    results = []
    for attendance in attendances:
        results.append({
            'date': attendance.date.strftime('%Y-%m-%d'),
            'status': attendance.status
        })
    return jsonify(results), 200



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

        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)  # Add timeout
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, sms_email, msg.as_string())
        server.quit()

        print(f"✅ SMS sent successfully to {phone_number}")
        return True
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error for SMS: {e}")
        return False
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

        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)  # Add timeout
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, email, msg.as_string())
        server.quit()

        print(f"✅ Email sent successfully to {email}")
        return True
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error for email: {e}")
        return False
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False

# Attendance marking routes with notifications
@app.route('/mark_attendance', methods=['GET', 'POST'], endpoint='mark_attendance')
@login_required
def mark_attendance_page():
    if current_user.role != 'host':
        return redirect(url_for('login'))
    if request.method == 'POST':
        date_str = request.form.get('date')
        if not date_str:
            flash('Date is required')
            return redirect(url_for('mark_attendance_page'))
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        students = Student.query.all()
        for student in students:
            status = request.form.get(f'status_{student.id}', 'absent')
            attendance = Attendance.query.filter_by(student_id=student.id, date=date).first()
            if attendance:
                attendance.status = status
            else:
                attendance = Attendance(student_id=student.id, date=date, status=status)
                db.session.add(attendance)
        db.session.commit()

        # Send notifications to parents (non-blocking)
        try:
            for student in students:
                status = request.form.get(f'status_{student.id}', 'absent')
                parents = User.query.filter_by(student_id=student.id, role='parent').all()
                for parent in parents:
                    message = f"{student.name} is {status} on {date}"
                    try:
                        send_notification(parent, message)
                    except Exception as e:
                        print(f"Failed to send notification to parent {parent.username}: {e}")
                        # Continue processing other notifications
        except Exception as e:
            print(f"Error during notification sending: {e}")
            # Don't let notification failures affect the attendance marking

        flash('Attendance marked successfully!')
        return redirect(url_for('host_dashboard'))

    students = Student.query.all()
    return render_template('mark_attendance.html', students=students)

@app.route('/mark_attendance/<int:student_id>', methods=['POST'], endpoint='mark_single_attendance')
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
    # Send notifications to parents (non-blocking)
    try:
        for parent in parents:
            message = f"{student.name} is {status} on {date}"
            try:
                send_notification(parent, message)
            except Exception as e:
                print(f"Failed to send notification to parent {parent.username}: {e}")
                # Continue processing other notifications
    except Exception as e:
        print(f"Error during notification sending: {e}")
        # Don't let notification failures affect the attendance marking
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
                # Send notifications to parents (non-blocking)
                try:
                    for parent in parents:
                        message = f"{student.name} is {status} on {date}"
                        try:
                            send_notification(parent, message)
                        except Exception as e:
                            print(f"Failed to send notification to parent {parent.username}: {e}")
                            # Continue processing other notifications
                except Exception as e:
                    print(f"Error during notification sending: {e}")
                    # Don't let notification failures affect the attendance marking
    return redirect(url_for('host_dashboard'))

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

@app.route('/view_attendance')
@login_required
def view_attendance():
    if current_user.role != 'host':
        return redirect(url_for('login'))
    query = Attendance.query
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
        query = query.filter_by(date=request.args.get('date'))
    if request.args.get('status'):
        query = query.filter_by(status=request.args.get('status'))
    attendances = query.all()
    students = Student.query.all()
    sections = Section.query.all()
    return render_template('view_attendance.html', attendances=attendances, students=students, sections=sections)

@app.route('/export_csv')
@login_required
def export_csv():
    if current_user.role != 'host':
        return redirect(url_for('login'))
    query = Attendance.query
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
        query = query.filter_by(date=request.args.get('date'))
    if request.args.get('status'):
        query = query.filter_by(status=request.args.get('status'))
    attendances = query.all()

    # Create CSV response
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Student Name', 'Date', 'Status', 'Grade Level', 'Section'])

    for attendance in attendances:
        student = Student.query.get(attendance.student_id)
        section = Section.query.get(student.section_id) if student else None
        writer.writerow([
            student.name if student else 'Unknown',
            attendance.date.strftime('%Y-%m-%d'),
            attendance.status,
            student.grade_level if student else '',
            section.name if section else ''
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=attendance_export.csv'}
    )

@app.route('/attendance_report')
@login_required
def attendance_report():
    if current_user.role != 'host':
        return redirect(url_for('login'))
    query = Student.query
    if request.args.get('grade'):
        query = query.filter_by(grade_level=int(request.args.get('grade')))
    if request.args.get('section'):
        query = query.filter_by(section_id=int(request.args.get('section')))
    students = query.all()
    report_data = []
    for student in students:
        attendances = Attendance.query.filter_by(student_id=student.id).all()
        total_days = len(attendances)
        present_days = len([a for a in attendances if a.status == 'present'])
        absent_days = len([a for a in attendances if a.status == 'absent'])
        tardy_days = len([a for a in attendances if a.status == 'tardy'])
        percentage = (present_days / total_days * 100) if total_days > 0 else 0
        report_data.append({
            'name': student.name,
            'total': total_days,
            'present': present_days,
            'absent': absent_days,
            'tardy': tardy_days,
            'percentage': round(percentage, 2)
        })
    sections = Section.query.all()
    return render_template('attendance_report.html', report_data=report_data, sections=sections)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
