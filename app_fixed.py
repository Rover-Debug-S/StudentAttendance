from flask import Flask, render_template, request, redirect, url_for, Response, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from datetime import datetime
from db import db
import csv
import io
from werkzeug.security import generate_password_hash, check_password_hash
from twilio.rest import Client
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
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
        user = User.query.filter_by(username=username).first()
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
SMS_METHOD = os.environ.get('SMS_METHOD', 'console')  # Options: console, email, file

# For console mode (FREE - just prints to terminal)
# For email mode (FREE - uses your email)
EMAIL_USER = os.environ.get('EMAIL_USER')
EMAIL_PASS = os.environ.get('EMAIL_PASS')
SMS_GATEWAY = os.environ.get('SMS_GATEWAY', 'tmomail.net')

def send_sms_notification(phone_number, message):
    """Send SMS notification using configured method"""
    if SMS_METHOD == 'console':
        # FREE - Just print to console (for testing)
        print(f"📱 SMS to {phone_number}: {message}")
        return True

    elif SMS_METHOD == 'email' and EMAIL_USER and EMAIL_PASS:
        # FREE - Send email to SMS gateway
        try:
            import smtplib
            from email.mime.text import MIMEText

            # Convert phone to email format (e.g., 1234567890@tmomail.net)
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

            print(f"✅ SMS sent to {phone_number} via email")
            return True
        except Exception as e:
            print(f"❌ SMS failed: {e}")
            return False

    elif SMS_METHOD == 'file':
        # Save to file for testing
        with open('sms_log.txt', 'a') as f:
            f.write(f"{datetime.now()}: SMS to {phone_number}: {message}\n")
        print(f"📄 SMS logged to file: {message}")
        return True

    else:
        print(f"⚠️ SMS method '{SMS_METHOD}' not configured")
        return False

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

# Import the simple OCR module
from ocr_simple import TESSERACT_AVAILABLE, process_attendance_image

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
                # Get all students for comparison
                all_students = Student.query.all()

                # Process the image using our simple OCR module
                matched_students, detected_student_ids, recognized_names, error = process_attendance_image(file, all_students)

                if error:
                    flash(error)
                    return redirect(request.url)

                # If no students matched, show all students with a warning
                if not matched_students:
                    flash('No student names were recognized in the image. Please check image quality or try manual marking.')
                    matched_students = all_students
                    detected_student_ids = []

                # Render review page with only matched students
                return render_template('review_attendance.html',
                                     date=date,
                                     students=matched_students,
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
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    students = Student.query.all()
    for student in students:
        status = request.form.get(f'status_{student.id}', 'absent')
        attendance = Attendance(student_id=student.id, date=date, status=status)
        db.session.add(attendance)
    db.session.commit()
    # Send SMS notification to parents using the configured method
    for student in students:
        for parent in student.parents:
            if parent.role == 'parent' and parent.mobile:
                status = request.form.get(f'status_{student.id}', 'absent')
                message = f"Attendance update for {student.name} on {date}: {status.capitalize()}"
                send_sms_notification(parent.mobile, message)
    return redirect(url_for('host_dashboard'))

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

    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Student Name', 'Grade', 'Section', 'Date', 'Status'])
    for attendance in attendances:
        cw.writerow([attendance.student.name, attendance.student.grade_level, attendance.student.section.name, attendance.date, attendance.status])

    output = si.getvalue()
    return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=attendance.csv"})

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

# Parent registration
@app.route('/parent_login', methods=['GET', 'POST'])
def parent_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password) and user.role == 'parent':
            login_user(user)
            return redirect(url_for('parent_dashboard'))
        flash('Invalid username or password')
    return render_template('parent_login.html')

@app.route('/parent_register', methods=['GET', 'POST'])
def parent_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        student_id = request.form['student_id']
        mobile = request.form['mobile']

        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('parent_register'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists')
            return redirect(url_for('parent_register'))

        # Verify student_id exists
        student = Student.query.get(student_id)
        if not student:
            flash('Selected student does not exist')
            return redirect(url_for('parent_register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password, role='parent', student_id=student_id, mobile=mobile)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful, please login')
        return redirect(url_for('login'))
    students = Student.query.all()
    return render_template('parent_register.html', students=students)

# API for mobile app
@app.route('/api/parent_login', methods=['POST'])
def api_parent_login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password) or user.role != 'parent':
        return {'error': 'Invalid credentials'}, 401
    return {'user_id': user.id}, 200

@app.route('/api/parent_register', methods=['POST'])
def api_parent_register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    student_id = data['student_id']
    mobile = data['mobile']
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return {'error': 'Username exists'}, 400
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(username=username, password=hashed_password, role='parent', student_id=student_id)
    db.session.add(new_user)
    db.session.commit()
    return {'message': 'Registered'}, 201

@app.route('/api/parent_dashboard/<int:user_id>')
def api_parent_dashboard(user_id):
    user = User.query.get(user_id)
    if not user or user.role != 'parent':
        return {'error': 'User not found'}, 404
    return {
        'student_name': user.student.name,
        'mobile': user.mobile
    }, 200

@app.route('/api/update_mobile/<int:user_id>', methods=['POST'])
def api_update_mobile(user_id):
    user = User.query.get(user_id)
    if not user or user.role != 'parent':
        return {'error': 'User not found'}, 404
    data = request.get_json()
    user.mobile = data['mobile']
    db.session.commit()
    return {'message': 'Updated'}, 200

@app.route('/api/search_students')
def api_search_students():
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return [], 200

    students = Student.query.filter(Student.name.ilike(f'%{query}%')).all()
    results = []
    for student in students:
        results.append({
            'id': student.id,
            'name': student.name,
            'grade_level': student.grade_level,
            'section_name': student.section.name if student.section else 'No Section'
        })
    return results, 200

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

def create_default_host():
    host = User.query.filter_by(username='host').first()
    if not host:
        hashed_password = generate_password_hash('host123', method='pbkdf2:sha256')
        host = User(username='host', password=hashed_password, role='host')
        db.session.add(host)
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # create_default_host()  # Commented out to hide default host credentials
    app.run(host='0.0.0.0', port=5000, debug=True)
