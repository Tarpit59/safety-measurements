from base import app, db
from base.com.vo.helmet_vest_detection_vo import HelmetVestDetectionVO


class HelmetVestDetectionDAO():
    def save(self, helmet_vest_detection_vo_obj):
        db.session.add(helmet_vest_detection_vo_obj)
        db.session.commit()
