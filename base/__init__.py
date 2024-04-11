from flask import Flask, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.http import parse_range_header

app = Flask(__name__)
app.config['SECRET_KEY'] = 'habbd6ag63y628##4#t6&&*89*^%$fGbVGFFnN%5$'
 
login_manager = LoginManager()
login_manager.init_app(app)

# Configure MySQL database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:3306/safety_measurements_2?charset=utf8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Path configuration
app.config['SAFETY_MODEL'] = r"model\best.pt"
app.config['RESTRICTED_MODEL'] = r"model\yolov8n.pt"

app.config['RESTRICTED_UPLOAD_FOLDER'] = r'base\static\upload\restricted'
app.config['FIRST_FRAME_FOLDER'] = r'base\static\first_frame'
app.config['SAFETY_UPLOAD_FOLDER'] = r'base\static\upload\safety'

app.config['RESTRICTED_OUTPUT_FOLDER'] = r'base\static\output\restricted'
app.config['SAFETY_OUTPUT_FOLDER'] = r'base\static\output\safety'

# Database instance
db = SQLAlchemy(app)

from base.com import controller