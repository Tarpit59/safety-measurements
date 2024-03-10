import os
from werkzeug.utils import secure_filename
from flask import render_template, redirect, request
from flask_login import login_user, login_required, current_user
from base.com.service.safety_service import apply_safety_detection
from base import app


@app.route('/safety-detection', methods=['GET', 'POST'])
@login_required
def safety_detection():
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

                # Redirect to the safety_result route with the results as query parameters
                    return redirect(url_for('safety_result',
                                            video_name=video_name,
                                            safety_percentage=safety_percentage,
                                            unsafety_percentage=unsafety_percentage))
                finally:
                    os.remove(video_path)
                    
            return app.config['UPLOAD_FOLDER']
    except Exception as e:
        return render_template('error.html', error=e)
