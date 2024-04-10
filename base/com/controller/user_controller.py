from flask import render_template, redirect, request, session
from flask_login import login_user, login_required, current_user, logout_user
from base import app, login_manager
from base.com.vo.user_vo import UserVO
from base.com.dao.user_dao import UserDAO


@login_manager.user_loader
def loader_user(login_id):
    return UserVO.query.get(login_id)


@app.login_manager.unauthorized_handler
def unauth_handler():
    return redirect('login')


@app.route('/')
def index():
    try:
        return redirect('login')
    except Exception as e:
        return render_template('error.html', error=e)


@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        user_dao = UserDAO()
        user_vo = UserVO()
        if request.method == 'GET':
            return render_template('user/login.html')
        else:
            username = request.form.get('username')
            password = request.form.get('password')
            user_vo.login_username = username
            user_vo.login_password = password
            user = user_dao.view_one_user(user_vo)
            if user:
                login_user(user)
                return redirect('/dashboard')
            return render_template('user/login.html', credentials="Invalid  Credentials")
    except Exception as e:
        return render_template('error.html', error=e)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)


@app.route("/logout")
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
        session.clear()
    return redirect('login')
