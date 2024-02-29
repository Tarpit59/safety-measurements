from base import db
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from base.com.vo.user_model import User
from flask_login import UserMixin

class SafetyData(db.Model):
    __tablename__ = 'safety_data'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('login.id'), nullable=False)
    user = relationship(User)
    video_name = Column(String(255), nullable=False)
    safety_percentage = Column(Float, nullable=False)
    unsafety_percentage = Column(Float, nullable=False)
    
    def __init__(self, user_id, video_name, safety_percentage, unsafety_percentage, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.video_name = video_name
        self.safety_percentage = safety_percentage
        self.unsafety_percentage = unsafety_percentage

    def __repr__(self):
        return f"<SafetyData(id={self.id}, user_id={self.user_id}, video_name={self.video_name}, safety_percentage={self.safety_percentage}, unsafety_percentage={self.unsafety_percentage})>"
