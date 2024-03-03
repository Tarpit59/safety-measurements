from base import db, app
from flask_login import UserMixin

class UserVO(db.Model, UserMixin):
    __tablename__ = 'user_table'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def as_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password
        }


with app.app_context():
    db.create_all()
