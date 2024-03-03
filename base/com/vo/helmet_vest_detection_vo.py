from base import db, app


class HelmetVestDetectionVO(db.Model):
    __tablename__ = 'helmet_vest_detection_table'

    id = db.Column(db.Integer, primary_key=True)
    video_name = db.Column(db.String(255), nullable=False)
    safety_percentage = db.Column(db.Float, nullable=False)
    unsafety_percentage = db.Column(db.Float, nullable=False)

    def as_dict(self):
        return {
            'id': self.id,
            'video_name': self.video_name,
            'safety_percentage': self.safety_percentage,
            'unsafety_percentage': self.unsafety_percentage
        }


with app.app_context():
    db.create_all()
