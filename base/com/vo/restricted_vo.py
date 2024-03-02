from base import db


class RestrictedAreaVO(db.Model):
    __tablename__ = 'restricted_area_table'

    id = db.Column(db.Integer, primary_key=True)
    video_name = db.Column(db.String(255), nullable=False)
    person_count = db.Column(db.Integer, nullable=False)

    def as_dict(self):
        return {
            'id': self.id,
            'video_name': self.video_name,
            'person_count': self.person_count
        }


with app.app_context():
    db.create_all()
