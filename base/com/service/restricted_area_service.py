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

def count_persons_entered_restricted_area(video, coordinates):
    # Initialize YOLO model
    model = YOLO("yolov8n.pt")
    names = model.names

    # Open video for processing
    video_capture = cv2.VideoCapture(video)

    # Initialize variables
    persons_entered_count = 0

    # Create a Shapely Polygon from the user-input coordinates
    restricted_area_shapely = Polygon(coordinates)
    while True:
        ret, frame = video_capture.read()

        if not ret:
            break
        frame = cv2.resize(frame, (720, 480))   
        results = model(frame, classes=[0])
        boxes = results[0].boxes

        for box in boxes:
            class_id = int(box.cpu().cls[0])
            x1, y1, x2, y2 = box.cpu().xyxy[0]

            x3, y3 = x1 + abs(x2 - x1), y1
            x4, y4 = x1, y1 + abs(y1 - y2)

            person_polygon_shapely = Polygon([(x1, y1), (x4, y4), (x2, y2), (x3, y3)])
            intersection_area = restricted_area_shapely.intersection(person_polygon_shapely).area
            union_area = restricted_area_shapely.union(person_polygon_shapely).area
            iou = intersection_area / union_area if union_area > 0 else 0

            if names.get(class_id) == 'person' and iou > 0.01:
                persons_entered_count += 1
    video_capture.release()
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