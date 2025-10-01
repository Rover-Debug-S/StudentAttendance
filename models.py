from db import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # hashed password
    role = db.Column(db.String(20), nullable=False)  # 'host' or 'parent'
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=True)  # only for parents
    mobile = db.Column(db.String(20), nullable=True)  # mobile number for parents
    email = db.Column(db.String(120), nullable=True)  # email for parents

class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    grade_level = db.Column(db.Integer, nullable=False)  # 7-12
    students = db.relationship('Student', backref='section', lazy=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    grade_level = db.Column(db.Integer, nullable=False)  # 7-12
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)
    attendances = db.relationship('Attendance', backref='student', lazy=True)
    parents = db.relationship('User', backref='student', lazy=True)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False)  # 'present', 'absent', or 'tardy'
