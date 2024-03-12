import os
from flask import render_template, redirect, request, url_for, jsonify, session
from flask_login import login_user, login_required, current_user
from base.com.service.restricted_area_service import get_first_frame, store_uploaded_video, count_persons_entered_restricted_area
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

            return redirect(url_for('define_area', video_path=video_path, first_frame_path=first_frame_path))
        return render_template('error.html', error="Method not available")
    except Exception as e:
        return render_template('error.html', error=e)


@app.route('/define_area', methods=['GET', 'POST'])
@login_required
def define_area():
    try:
        video_path = request.args.get('video_path', None)
        first_frame_path = request.args.get('first_frame_path', None)

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


@app.route('/process_restricted_area', methods=["GET", "POST"])
@login_required
def process_restricted_area():
    try:
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

            # Implement your AI code for person counting using the coordinates
            # Example: pass coordinates to the AI function and get the result
            person_count = count_persons_entered_restricted_area(
                video_path, converted_coordinates)
            # Store person_count in the session
            session['person_count'] = person_count
            # Redirect to the restricted_area_result route with the person count as a parameter
            return jsonify({'success': True, 'person_count': person_count})

        else:
            raise ValueError('Invalid or missing coordinates in the request')

    except Exception as e:
        return render_template('error.html', error=e)


@app.route('/restricted_area_result', methods=["GET"])
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
            video_name=latest_uploaded_file,
            video="static/output/output_video.mp4",
            user=current_user
        )
    except Exception as e:
        return render_template('error.html', error=e)
