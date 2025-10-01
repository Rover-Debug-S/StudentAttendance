import os
from db import db
from app import app
from models import Student, Attendance, User, Section

# Delete the database file if it exists
db_path = os.path.join(os.path.dirname(__file__), 'attendance.db')
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"Deleted existing database file: {db_path}")

with app.app_context():
    # Drop all tables (in case file wasn't deleted)
    try:
        db.drop_all()
    except Exception as e:
        print(f"Error dropping tables: {e}")

    # Create all tables with new schema
    db.create_all()

    # Create default host user
    from werkzeug.security import generate_password_hash
    host = User(username='host', password=generate_password_hash('host123', method='pbkdf2:sha256'), role='host')
    db.session.add(host)
    db.session.commit()

    print("Database reset complete with new schema!")
