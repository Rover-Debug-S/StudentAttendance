from app import app, db, create_default_host
from models import User

with app.app_context():
    db.create_all()
    create_default_host()
    print("Default host created.")
