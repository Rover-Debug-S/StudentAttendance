from app import app, db, create_default_data
from models import User

with app.app_context():
    db.create_all()
    create_default_data()
    print("Default data created.")
