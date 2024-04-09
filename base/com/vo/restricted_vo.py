from base import db, app


class RestrictedAreaVO(db.Model):
    __tablename__ = 'restricted_area_table'

    id = db.Column(db.Integer, primary_key=True)
    video_name = db.Column(db.String(255), nullable=False)
    person_count = db.Column(db.Integer, nullable=False)
    person_id = db.Column(db.Integer, nullable=True)
    entry_time = db.Column(db.String(255), nullable=True)
    exit_time = db.Column(db.String(255), nullable=True)

    def as_dict(self):
        return {
            'id': self.id,
            'video_name': self.video_name,
            'person_count': self.person_count,
            'person_id': self.person_id,
            'entry_time': self.entry_time,
            'exit_time': self.exit_time
        }


with app.app_context():
    db.create_all()
