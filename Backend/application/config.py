class Config:
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class LocalDevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://hms_user:strongpassword@localhost:5432/hms_db"
    )
    JWT_SECRET_KEY = "potla-the-scout"