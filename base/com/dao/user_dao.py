from base import app, db
from base.com.vo.user_vo import UserVO


class UserDAO():
    def view_one_user(self, user_vo):
        return UserVO.query.filter_by(username=user_vo.username, 
            password=user_vo.password).first()
