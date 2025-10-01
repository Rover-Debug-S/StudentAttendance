import os
from db import db
from app import app
from models import User

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'attendance.db'))
with open('db_check_output.txt', 'w') as f:
    f.write(f"Database path: {db_path}\n")
    f.write(f"Database exists: {os.path.exists(db_path)}\n")

with app.app_context():
    users = User.query.all()
    with open('db_check_output.txt', 'a') as f:
        f.write(f"Number of users: {len(users)}\n")
        for user in users:
            f.write(f"User: {user.username}, Role: {user.role}\n")
