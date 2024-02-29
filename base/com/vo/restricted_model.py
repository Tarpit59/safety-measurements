from base import db
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from base.com.vo.user_model import User
from flask_login import UserMixin

class RestrictedAreaData(db.Model):
    __tablename__ = 'restricted_area_data'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('login.id'), nullable=False)
    user = relationship(User)
    video_name = Column(String(255), nullable=False)
    person_count = Column(Integer, nullable=False)

    def __init__(self, user_id, video_name, person_count, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.video_name = video_name
        self.person_count = person_count

    def __repr__(self):
        return f"<RestrictedAreaData(id={self.id}, user_id={self.user_id}, video_name={self.video_name}, person_count={self.person_count})>"
