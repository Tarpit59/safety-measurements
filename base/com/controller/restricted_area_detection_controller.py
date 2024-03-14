import os
from flask import render_template, redirect, request, url_for, jsonify, session
from flask_login import login_required, current_user
from base.com.service.restricted_area_service import get_first_frame, store_uploaded_video, count_persons_entered_restricted_area
from base.com.vo.restricted_vo import RestrictedAreaVO
from base.com.dao.restricted_area_detection_dao import RestrictedAreaDAO
from base import app


@app.route('/restricted-area-detection', methods=['GET', 'POST'])
@login_required
def restricted_area_detection():
    try:
        if request.method == 'GET':
            return render_template('restricted_area_detection/index.html', user=current_user)
        elif request.method == 'POST':
            video = request.files.get('video')

            video_path = store_uploaded_video(video)
            first_frame_path = get_first_frame(video_path)

            session['video_path'] = video_path
            session['first_frame_path'] = first_frame_path

            return redirect('define-area')
        return render_template('error.html', error="Method not available")
    except Exception as e:
        return render_template('error.html', error=e)


@app.route('/define-area', methods=['GET', 'POST'])
@login_required
def define_area():
    try:
        video_path = session.get('video_path')
        first_frame_path = session.get('first_frame_path')

        if video_path is None or first_frame_path is None:
            return redirect('restricted-area-detection')

        if request.method == 'POST':
            video = request.files['video']
            video_path = store_uploaded_video(video)
            first_frame_path = get_first_frame(video_path)
        elif request.method == 'GET':
            return render_template(
                'restricted_area_detection/define_area.html',
                video_path=video_path,
                first_frame_path=first_frame_path,
                user=current_user
            )

        return render_template('error.html', error="Method not allowed")
    except Exception as e:
        return render_template('error.html', error=e)
    finally:
        session.clear()


@app.route('/process-restricted-area', methods=['GET', "POST"])
@login_required
def process_restricted_area():
    restricted_area_vo_obj = RestrictedAreaVO()
    restricted_area_dao_obj = RestrictedAreaDAO()
    try:
        if request.method != 'POST':
            return redirect('restricted-area-detection')

        data = request.json
        # Ensure data is a dictionary and has 'coordinates' key
        if isinstance(data, dict) and 'coordinates' in data:
            coordinates = data['coordinates']
            # Convert coordinates to the desired format [(x1, y1), (x2, y2), ...]
            converted_coordinates = [(round(coord['x']), round(
                coord['y'])) for coord in coordinates if 'x' in coord and 'y' in coord]
            # Automatically detect the video path from the uploaded files in the UPLOAD_FOLDER
            uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
            if uploaded_files:
                # Assuming the latest uploaded file is the one to be processed
                latest_uploaded_file = max(
                    uploaded_files,
                    key=lambda f: os.path.getctime(
                        os.path.join(app.config['UPLOAD_FOLDER'], f))
                )
                video_path = os.path.join(
                    app.config['UPLOAD_FOLDER'], latest_uploaded_file)

            person_count = count_persons_entered_restricted_area(
                video_path,
                converted_coordinates
            )

            restricted_area_vo_obj.person_count = person_count
            restricted_area_vo_obj.video_name = latest_uploaded_file
            restricted_area_dao_obj.save(restricted_area_vo_obj)

            # Store person_count in the session
            session['person_count'] = person_count
            # Redirect to the restricted_area_result route with the person count as a parameter
            return jsonify({'success': True, 'person_count': person_count})
        else:
            raise ValueError('Invalid or missing coordinates in the request')
    except Exception as e:
        return render_template('error.html', error=e)


@app.route('/restricted-area-result', methods=["GET"])
@login_required
def restricted_area_result():
    try:
        person_count = session.get('person_count', default=0)
        uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])

        if uploaded_files:
            # Assuming the latest uploaded file is the one to be processed
            latest_uploaded_file = max(
                uploaded_files, key=lambda f: os.path.getctime(os.path.join(app.config['UPLOAD_FOLDER'], f)))
        # latest_uploaded_file_new=latest_uploaded_file
        os.remove(os.path.join(
            app.config['UPLOAD_FOLDER'], latest_uploaded_file))

        return render_template(
            'restricted_area_detection/result.html',
            person_count=person_count,
            video_name=latest_uploaded_file.upper(),
            video="static/output/output_restricted/output_video.mp4",
            user=current_user
        )
    except Exception as e:
        return redirect('restricted-area-detection')
