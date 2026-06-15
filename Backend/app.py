from flask import Flask
from application.config import LocalDevelopmentConfig
from application.database import db
from application.models import User, RoleEnum
from application.extensions import migrate
from application.security import jwt
from flask_cors import CORS
from application.celery_init import celery_init_app
from celery.schedules import crontab

app = None

def create_app():
    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    app.app_context().push()
    return app

app = create_app()
celery = celery_init_app(app)
celery.autodiscover_tasks()

from application.routes import *

def create_admin_if_not_exists():
    admin_email = "batman@admin.com"
    existing_admin = User.query.filter_by(email=admin_email).first()
    
    if existing_admin is None:
        admin = User(
            username="batman",
            email=admin_email,
            role=RoleEnum.admin
        )
        admin.set_password("12345")
        db.session.add(admin)
        db.session.commit()
        print(f"[INFO] Admin user {admin_email} created.")
    else:
        print(f"[INFO] Admin user {admin_email} already exists.")

if __name__ == "__main__":
    with app.app_context():
        create_admin_if_not_exists()
    app.run(debug=True)