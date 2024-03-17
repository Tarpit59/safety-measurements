import os
from ultralytics import YOLO
import cv2
import logging
from base.com.vo.helmet_vest_detection_vo import HelmetVestDetectionVO
from base import db
import tempfile
import shutil
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Consider moving model initialization outside the function and make it a configurable parameter
MODEL_PATH = r"model\best.pt"
OUTPUT_FOLDER = r"base\static\output"
OUTPUT_VIDEO_PATH = r"base\static\output\output_video.mp4"


def initialize_model():
    return YOLO(MODEL_PATH)


def draw_text_and_box_on_image(image, text, position, box_coordinates, font, color):
    draw = ImageDraw.Draw(image)

    # Draw bounding box
    draw.rectangle(box_coordinates, outline=color, width=2)

    # Draw text with specified color
    draw.text(position, text, fill=color, font=font)

    return image


def apply_safety_detection(video):
    model = initialize_model()

    # Create a temporary directory to store the video
    temp_dir = tempfile.mkdtemp()
    video_name = os.path.basename(video)
    temp_video_path = os.path.join(temp_dir, os.path.basename(video))
    try:
        # Copy the uploaded video to the temporary folder
        shutil.copy(video, temp_video_path)

        # Open the video capture
        cap = cv2.VideoCapture(temp_video_path)

        # Get the frames per second (fps) of the input video
        fps = cap.get(cv2.CAP_PROP_FPS)
        # Create output folder if it doesn't exist
        if not os.path.exists(OUTPUT_FOLDER):
            os.makedirs(OUTPUT_FOLDER)

        # Create VideoWriter object with the same fps as the input video
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        # fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')

        out = cv2.VideoWriter(OUTPUT_VIDEO_PATH, fourcc,
                              fps, (int(cap.get(3)), int(cap.get(4))))

        frame_number = 0

        frame_number = 0
        safety_count = 0
        unsafety_count = 0

    # try:
        while True:
            # Read a frame from the video
            ret, frame = cap.read()

            # Break the loop if the video has ended
            if not ret:
                break

            # Convert the OpenCV BGR image to RGB (PIL format)
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            try:
                results = model.predict(frame)
                result = results[0]

                # Create a font with the desired size
                font_size = 20  # Adjust the font size as needed
                # Use arial.ttf or another font file with the desired size
                font = ImageFont.truetype("arial.ttf", font_size)

                # Keep track of whether any detection occurred in this frame
                detection_occurred = False

                safety_classes = ["Vest", "Helmet"]
                for idx, box in enumerate(result.boxes):
                    class_id = result.names[box.cls[0].item()]
                    # conf = box.conf[0].item()
                    cords = box.xyxy[0].tolist()
                    cords = [round(x) for x in cords]
                    conf = round(box.conf[0].item(), 2)

                    # Determine color based on class_id
                    if class_id == "Helmet":
                        bounding_box_color = (0, 255, 0)  # Green
                        text_color = (0, 255, 0)  # Green
                    elif class_id == "NOHelmet":
                        bounding_box_color = (0, 0, 255)  # Blue
                        text_color = (0, 0, 255)  # Blue
                    elif class_id == "NOVest":
                        bounding_box_color = (255, 0, 0)  # Red
                        text_color = (255, 0, 0)  # Red
                    elif class_id == "Vest":
                        bounding_box_color = (255, 255, 0)  # Yellow
                        text_color = (255, 255, 0)  # Yellow
                    else:
                        bounding_box_color = (128, 128, 128)  # Default to gray
                        text_color = (128, 128, 128)  # Default to gray

                    # Draw text and bounding box on the image
                    text = f"{class_id}({conf})"
                    # Adjust the position based on your preference
                    position = (cords[0], cords[1] - 22)
                    image_with_text_and_box = draw_text_and_box_on_image(
                        image, text, position, cords, font, text_color)

                    # Convert the modified image back to BGR (OpenCV format)
                    modified_frame = cv2.cvtColor(
                        np.array(image_with_text_and_box), cv2.COLOR_RGB2BGR)

                    # If at least one detection occurred, set detection_occurred to True
                    if not detection_occurred:
                        detection_occurred = True

                    if class_id in safety_classes:
                        safety_count += 1
                    else:
                        unsafety_count += 1

                # Write the frame to the output video (outside the detection loop)
                out.write(
                    modified_frame) if detection_occurred else out.write(frame)

            except Exception as e:
                # Log the error instead of printing
                logging.error(f"Error processing frame {frame_number}: {e}")

            frame_number += 1

    finally:
        # Release the video capture
        cap.release()

    # Calculate percentages based on the total number of detections
    total_detections = safety_count + unsafety_count

    # Check if total_detections is not zero before calculating percentages
    if total_detections != 0:
        safety_percentage = (safety_count / total_detections) * 100
        unsafety_percentage = (unsafety_count / total_detections) * 100
    else:
        return video_name, None, None

    return video_name, round(safety_percentage, 2), round(unsafety_percentage, 2)
