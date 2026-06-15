from flask_jwt_extended import JWTManager
from application.models import User

jwt = JWTManager()

@jwt.user_identity_loader
def load(user):
    return user.email

@jwt.user_lookup_loader
def user_lookup_callback(_jwtheader, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(email=identity).one_or_none()