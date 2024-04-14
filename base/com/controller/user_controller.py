from datetime import datetime
from flask import render_template, redirect, request, session, url_for
from flask_login import login_user, login_required, current_user, logout_user
from base import app, login_manager
from base.com.vo.user_vo import UserVO
from base.com.dao.user_dao import UserDAO
from base.com.vo.detection_vo import DetectionVO
from base.com.dao.detection_dao import DetectionDAO


@login_manager.user_loader
def loader_user(login_id):
    return UserVO.query.get(login_id)


@app.login_manager.unauthorized_handler
def unauth_handler():
    return redirect('login')


@app.route('/')
def index():
    try:
        return redirect('login')
    except Exception as e:
        return render_template('error.html', error=e)


@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        user_dao = UserDAO()
        user_vo = UserVO()
        if request.method == 'GET':
            return render_template('user/login.html')
        else:
            username = request.form.get('username')
            password = request.form.get('password')
            user_vo.login_username = username
            user_vo.login_password = password
            user = user_dao.view_one_user(user_vo)
            if user:
                login_user(user)
                return redirect('/dashboard')
            return render_template('user/login.html', credentials="Invalid  Credentials")
    except Exception as e:
        return render_template('error.html', error=e)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)


@app.route('/view-detection', methods=['GET'])
@login_required
def view_detection():
    detection_dao_obj = DetectionDAO()
    try:
        if request.method == 'GET':
            detection_id = request.args.get('detection_id')
            if detection_id:
                detection_vo_obj = DetectionVO()
                detection_vo_obj.detection_id = detection_id
                detection_vo_obj.modified_by = current_user.login_id
                detection_vo_obj.is_deleted = True
                detection_vo_obj.modified_on = int(datetime.now().timestamp())
                
                detection_dao_obj.update_record(detection_vo_obj)

            data = detection_dao_obj.get_user_records()

            customized_data = []
            for i in range(len(data)):
                data_dict = {}

                data_dict['sr_no'] = i+1
                data_dict['detection_id'] = data[i].detection_id
                data_dict['detection_stats'] = data[i].detection_stats
                data_dict['input_file_path'] = data[i].input_file_path.split(
                    '\\')[-1].capitalize()
                data_dict['output_file_path'] = data[i].output_file_path.split(
                    '\\')[-1].capitalize()
                data_dict['detection_type'] = data[i].detection_type.capitalize()
                data_dict['detection_source'] = data[i].detection_source.capitalize()
                data_dict['detection_datetime'] = datetime.utcfromtimestamp(
                    data[i].detection_datetime).strftime('%Y-%m-%d %H:%M:%S')
                customized_data.append(data_dict)

            return render_template('user/view_detection.html', user=current_user, data=customized_data)

    except Exception as e:
        return render_template('error.html', error=e)


@app.route("/logout")
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
        session.clear()
    return redirect('login')
