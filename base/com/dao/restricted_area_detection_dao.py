from base import app, db
from base.com.vo.restricted_vo import RestrictedAreaVO


class RestrictedAreaDAO():
    def save(self, restricted_area_detection_vo_obj):
        db.session.add(restricted_area_detection_vo_obj)
        db.session.commit()
