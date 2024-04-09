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

# Upload folder path
UPLOAD_FOLDER = 'base/static/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database instance
db = SQLAlchemy(app)

from base.com import controller