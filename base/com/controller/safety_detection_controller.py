import os
from werkzeug.utils import secure_filename
from flask import render_template, request, session
from flask_login import login_required, current_user
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
                    result = apply_safety_detection(
                        video_path)
                    video_name, safety_percentage, unsafety_percentage = result
                    helmet_vest_detection_vo_obj.video_name = video_name
                    helmet_vest_detection_vo_obj.safety_percentage = safety_percentage
                    helmet_vest_detection_vo_obj.unsafety_percentage = unsafety_percentage

                    helmet_vest_detection_dao_obj.save(
                        helmet_vest_detection_vo_obj)

                    return render_template('safety_detection/result.html',
                                           user=current_user,
                                           video=f"static/output/output_safety/output_video.mp4",
                                           video_name=video_name.upper(),
                                           safety_percentage=safety_percentage,
                                           unsafety_percentage=unsafety_percentage
                                           )
                finally:
                    os.remove(video_path)
                    session.clear()

            return render_template('error.html', error="Video not available")
    except Exception as e:
        return render_template('error.html', error=e)
