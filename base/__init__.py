from flask import Flask, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.http import parse_range_header

app = Flask(__name__)
app.config['SECRET_KEY'] = 'habbd6ag63y628##4#t6&&*89*^%$fGbVGFFnN%5$'
 
login_manager = LoginManager()
login_manager.init_app(app)

# Configure MySQL database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:3307/internship'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Upload folder path
UPLOAD_FOLDER = 'base/static/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['STATIC_FOLDER'] = 'static'

# Database instance
db = SQLAlchemy(app)

# Partial content response function
# def partial_content_response(file, file_size, range_request, headers):
#     # Parse the Range header
#     ranges = parse_range_header(range_request, file_size)

#     # Check if the ranges are valid
#     if ranges is None or not ranges:
#         # Invalid range, return 416 Range Not Satisfiable
#         return Response(status=416, headers=headers)

#     # Extract the first range
#     first_range = ranges[0] if isinstance(ranges, list) else ranges
    
#     # Check the structure of the 'Range' object
#     if isinstance(first_range, tuple):
#         start, end = first_range
#     else:
#         # If 'Range' is not a tuple, it's assumed to be an integer
#         start = first_range.start if hasattr(first_range, 'start') else 0
#         end = first_range.stop - 1 if hasattr(first_range, 'stop') else file_size - 1

#     # Set the appropriate Content-Range header
#     headers['Content-Range'] = f'bytes {start}-{end}/{file_size}'

#     # Calculate the length of the content to be served
#     content_length = end - start + 1

#     # Move the file cursor to the specified start position
#     file.seek(start)

#     # Read the specified content from the file
#     content = file.read(content_length)

#     # Create a partial content response
#     response = Response(content, status=206, headers=headers)

#     return response

from base.com import controller