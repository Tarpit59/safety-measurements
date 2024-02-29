from base.com.vo.user_model import User
from flask import render_template, request, redirect, url_for, flash, send_file, send_from_directory, render_template_string, jsonify
from base import app, db
from flask_login import login_required, logout_user, current_user
from base.com.service.safety_service import apply_safety_detection
from werkzeug.utils import secure_filename
import os
from os.path import basename
from flask import session
from flask_login import login_user
from flask import send_from_directory
from flask import Response
from base import partial_content_response
from base.com.service.restricted_area_service import count_persons_entered_restricted_area, store_uploaded_video, get_first_frame
import logging

# Add the following lines to enable logging
logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)

# Define a configurable output directory for videos
OUTPUT_DIRECTORY = 'static/output'
UPLOAD_FOLDER = r"D:\projects\safety measurements\base\static\upload"
output_video_path = os.path.join(OUTPUT_DIRECTORY, 'output_video.mp4')
@app.route('/')
def index():
    return render_template('login.html')

# Sample route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            login_user(user)
            session['user_id'] = user.id
            # Successful login, redirect to the main page
            flash('Login successful!', 'success')
            return redirect(url_for('main_page'))
        else:
            # Invalid credentials, show an error message
            flash('Invalid username or password', 'error')

    return render_template('login.html')# Sample route for the main page after login

@app.route('/main_page')
@login_required
def main_page():
    return render_template('main_page.html')

@app.route("/safety_detection", methods=["GET", "POST"])
@login_required
def safety_detection():
    if request.method == "POST":
        video = request.files['video']

        if video:
            # Ensure the 'uploads' folder exists
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])

            # Generate a secure filename and save the video to the 'uploads' folder
            filename = secure_filename(video.filename)
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
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

            except Exception as e:
                print(f"Error processing safety detection: {e}")
                flash('Error applying safety detection!', 'error')
            finally:
                # Delete the uploaded video
                os.remove(video_path)


    return render_template('safety_detection.html')

@app.route("/safety_result", methods=["GET"])
@login_required
def safety_result():
    # Retrieve parameters from the query string or request data
    video_path = request.args.get('video_name')
    safety_percentage = float(request.args.get('safety_percentage'))
    unsafety_percentage = float(request.args.get('unsafety_percentage'))

    # Format the percentages to display only two decimal places
    formatted_safety_percentage = "{:.2f}".format(safety_percentage)
    formatted_unsafety_percentage = "{:.2f}".format(unsafety_percentage)

    # Extract only the video name from the path
    video_name = basename(video_path)

    # Render the safety_result.html template with the formatted results
    return render_template('safety_result.html',
                           video_name=video_name,
                           safety_percentage=formatted_safety_percentage,
                           unsafety_percentage=formatted_unsafety_percentage)

@app.route('/download_output_video')
def download_output_video():
    directory = os.path.dirname(output_video_path)
    downloadable_filename = 'output_video.mp4'  # Specify the desired filename

    return send_from_directory(directory, downloadable_filename, as_attachment=True)

@app.route('/view_safety_video')
@login_required
def view_safety_video():
    video_directory = r"D:\projects\safety measurements\base\static\output"
    video_filename = 'output_video.mp4'
    video_path = os.path.join(video_directory, video_filename)

    # Set response headers
    headers = {
        'Content-Type': 'video/mp4',
        'Accept-Ranges': 'bytes',
    }

    # Check for range request
    range_request = request.headers.get('Range')
    if range_request:
        video_file = open(video_path, 'rb')
        response = partial_content_response(video_file, os.path.getsize(video_path), range_request, headers)
        video_file.close()
    else:
        response = send_from_directory(video_directory, video_filename, mimetype='video/mp4', conditional=True, add_etags=True, headers=headers)

    return response

@app.route("/restricted_area_detection", methods=["GET", "POST"])
@login_required
def restricted_area_detection():
    if request.method == "POST":
        video = request.files['video']

        # Store the uploaded video and get the video path
        video_path = store_uploaded_video(video)
        # Get the first frame image path
        first_frame_path = get_first_frame(video_path)

        # Redirect to the 'define_area' route with the video_path
        return redirect(url_for('define_area', video_path=video_path, first_frame_path=first_frame_path))

    return render_template('restricted_area_detection.html')

@app.route('/define_area', methods=['GET', 'POST'])
def define_area():
    video_path = request.args.get('video_path', None)
    first_frame_path = request.args.get('first_frame_path', None)
    print("VID", video_path)

    if request.method == 'POST':
        video = request.files['video']
        video_path = store_uploaded_video(video)
        first_frame_path = get_first_frame(video_path)
        print("First Frame Path:", first_frame_path)

    return render_template('define_area.html', video_path=video_path, first_frame_path=first_frame_path)

@app.route('/process_restricted_area', methods=["GET", "POST"])
def process_restricted_area():
    try:
        # Assuming the coordinates are in the JSON request
        data = request.json

        # Ensure data is a dictionary and has 'coordinates' key
        if isinstance(data, dict) and 'coordinates' in data:
            coordinates = data['coordinates']

            # Print received coordinates for debugging
            # print("Received Coordinates:", coordinates)
            # Convert coordinates to the desired format [(x1, y1), (x2, y2), ...]
            converted_coordinates = [(round(coord['x']), round(coord['y'])) for coord in coordinates if 'x' in coord and 'y' in coord]

            # Log the converted coordinates for debugging
            print("Converted Coordinates:", converted_coordinates)
            # Automatically detect the video path from the uploaded files in the UPLOAD_FOLDER
            uploaded_files = os.listdir(UPLOAD_FOLDER)
            
            if uploaded_files:
                # Assuming the latest uploaded file is the one to be processed
                latest_uploaded_file = max(uploaded_files, key=lambda f: os.path.getctime(os.path.join(UPLOAD_FOLDER, f)))
                video_path = os.path.join(UPLOAD_FOLDER, latest_uploaded_file)

            # Implement your AI code for person counting using the coordinates
            # Example: pass coordinates to the AI function and get the result
            person_count = count_persons_entered_restricted_area(video_path, converted_coordinates)
            # print("PERSON_COUNT",person_count)
            # Store person_count in the session
            session['person_count'] = person_count
            # Redirect to the restricted_area_result route with the person count as a parameter
            return jsonify({'success': True, 'person_count': person_count})  
            
        else:
            raise ValueError('Invalid or missing coordinates in the request')

    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error in process_restricted_area: {str(e)}")

        # Return an error response
        return jsonify({'success': False, 'error': 'Internal Server Error'}), 500

@app.route('/restricted_area_result')
@login_required
def restricted_area_result():
    # Retrieve the person count from the session
    person_count = session.get('person_count', default=0)

    app.logger.debug(f"DEBUG - Person Count in restricted_area_result: {person_count}")
    
    # print("DEBUG - Person Count:", person_count)  # Add this line for debugging
    # Add any necessary logic for displaying the result page
    return render_template('restricted_area_result.html', person_count=person_count)

@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash('Logout successful!', 'success')
    else:
        flash('You are not logged in', 'error')
    
    return redirect(url_for("index"))

# from base.com.controller import routes
# login_user(user)