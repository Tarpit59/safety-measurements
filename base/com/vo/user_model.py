from base import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'login'  # Replace with your table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password