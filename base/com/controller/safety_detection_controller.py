from flask import render_template, redirect, request
from flask_login import login_user, login_required, current_user
from base import app


@app.route('/safety-detection', methods=['GET', 'POST'])
@login_required
def safety_detection():
    try:
        if request.method == 'GET':
            return render_template('safety_detection/index.html', user=current_user)
    except Exception as e:
        return render_template('error.html', error=e)
