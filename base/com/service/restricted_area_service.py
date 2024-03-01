# restricted_area_service.py
import cv2
import numpy as np
from shapely.geometry import Polygon
from ultralytics import YOLO
import os
from werkzeug.utils import secure_filename
from base.com.vo.restricted_model import RestrictedAreaData
from base import db
from flask import session

UPLOAD_FOLDER = r"D:\projects\safety measurements\base\static\upload"
FIRST_FRAME_FOLDER = r"D:\projects\safety measurements\base\static\first_frame"
OUTPUT_FOLDER = r"D:\projects\safety measurements\base\static\output"

def count_persons_entered_restricted_area(video, coordinates):
    # Initialize YOLO model
    model = YOLO("yolov8n.pt")
    names = model.names

    # Open video for processing
    video_capture = cv2.VideoCapture(video)
    fps = int(video_capture.get(cv2.CAP_PROP_FPS))

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'acv1')  # MP4V codec
    output_video_path = os.path.join(OUTPUT_FOLDER, 'output_video.mp4')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (720, 480))
    # Initialize variables
    persons_entered_count = 0

    # Create a Shapely Polygon from the user-input coordinates
    restricted_area_shapely = Polygon(coordinates)

    color_restricted_entered = (255, 0, 0)  # Blue
    color_restricted_empty = (255, 255, 255)  # White
    color_person_inside = (0, 0, 255)  # Red
    color_person_outside = (0, 255, 0)  # Green

    while True:
        ret, frame = video_capture.read()

        if not ret:
            break
        frame = cv2.resize(frame, (720, 480))   
        results = model(frame, classes=[0])
        boxes = results[0].boxes
        # Draw restricted area
        cv2.polylines(frame, [np.array(coordinates)], isClosed=True, color=color_restricted_empty, thickness=2)

        for box in boxes:
            class_id = int(box.cpu().cls[0])
            confidence = float(box.cpu().conf)
            x1, y1, x2, y2 = box.cpu().xyxy[0]

            x3, y3 = x1 + abs(x2 - x1), y1
            x4, y4 = x1, y1 + abs(y1 - y2)

            person_polygon_shapely = Polygon([(x1, y1), (x4, y4), (x2, y2), (x3, y3)])
            intersection_area = restricted_area_shapely.intersection(person_polygon_shapely).area
            union_area = restricted_area_shapely.union(person_polygon_shapely).area
            iou = intersection_area / union_area if union_area > 0 else 0

            # Check if person is inside or outside the restricted area
            if names.get(class_id) == 'person':
                if iou > 0.01:
                    persons_entered_count += 1
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color_person_inside, 2)
                    cv2.putText(frame, f'Confidence: {confidence:.2f}', (int(x1), int(y1) - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                    # Draw restricted area in blue when a person is inside
                    cv2.polylines(frame, [np.array(coordinates)], isClosed=True, color=color_restricted_entered,
                                  thickness=2)
                else:
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color_person_outside, 2)

        # Display count of persons entered in the top-left corner
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, f'Persons Entered: {persons_entered_count}', (10, 30), font, 0.8, (0, 255, 255), 2)

        # Write the frame to the output video
        out.write(frame)
    video_capture.release()
    out.release()
    store_restricted_area_data(video, persons_entered_count)
    return persons_entered_count

def store_uploaded_video(video):
    video_filename = secure_filename(video.filename)
    video_path = os.path.join(UPLOAD_FOLDER, video_filename)
    video.save(video_path)
    return video_path

def get_first_frame(video_path):
    cap = cv2.VideoCapture(video_path)
    _, frame = cap.read()
    frame = cv2.resize(frame, (720, 480))   
    frame_path = os.path.join(FIRST_FRAME_FOLDER, "first_frame.jpg")
    cv2.imwrite(frame_path, frame)
    cap.release()
    return frame_path

def store_restricted_area_data(video, persons_entered_count):
    # Retrieve user_id from the session or set it as needed
    user_id = session.get('user_id', 0)

    # Get the video name from the path
    video_name = os.path.basename(video)

    # Create a new RestrictedAreaData instance
    restricted_area_data = RestrictedAreaData(user_id=user_id, video_name=video_name, person_count=persons_entered_count)

    try:
        # Add the instance to the session
        db.session.add(restricted_area_data)

        # Commit changes to the database
        db.session.commit()

        print("Data successfully stored in the database.")

    except Exception as e:
        # Rollback changes in case of an error
        db.session.rollback()

        print(f"Error storing data in the database: {str(e)}")  