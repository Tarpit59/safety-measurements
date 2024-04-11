from base import app, db
from base.com.vo.detection_vo import DetectionVO


class HelmetVestDetectionDAO():
    def save(self, detection_vo_obj):
        db.session.add(detection_vo_obj)
        db.session.commit()
