import os
from werkzeug.utils import secure_filename
from flask import render_template, redirect, request,url_for
from flask_login import login_user, login_required, current_user
from base.com.service.safety_service import apply_safety_detection
from base.com.vo.helmet_vest_detection_vo import HelmetVestDetectionVO
from base.com.dao.safety_detection_dao import HelmetVestDetectionDAO
from base import app


@app.route('/safety-detection', methods=['GET', 'POST'])
@login_required
def safety_detection():
    helmet_vest_detection_vo_obj = HelmetVestDetectionVO()
    helmet_vest_detection_dao_obj = HelmetVestDetectionDAO()
    try:
        if request.method == 'GET':
            return render_template('safety_detection/index.html', user=current_user)
        elif request.method == 'POST':
            video = request.files.get('video')

            if video:
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])

                filename = secure_filename(video.filename)
                video_path = os.path.join(
                    app.config['UPLOAD_FOLDER'], filename)
                video.save(video_path)
                try:
                # Apply safety detection
                    results = apply_safety_detection(video_path)
                    video_name, safety_percentage, unsafety_percentage = results

                    helmet_vest_detection_vo_obj.video_name = video_name
                    helmet_vest_detection_vo_obj.safety_percentage = safety_percentage
                    helmet_vest_detection_vo_obj.unsafety_percentage = unsafety_percentage


                    helmet_vest_detection_dao_obj.save(helmet_vest_detection_vo_obj)

                    return render_template('safety_detection/result.html', user=current_user)
                finally:
                    os.remove(video_path)
                    
            return app.config['UPLOAD_FOLDER']
    except Exception as e:
        return render_template('error.html', error=e)