from flask import render_template, redirect, request, flash
from flask_login import login_user, login_required, current_user, logout_user
from base import app, login_manager
from base.com.vo.user_vo import UserVO
from base.com.dao.user_dao import UserDAO


@login_manager.user_loader
def loader_user(id):
    return UserVO.query.get(id)


@app.route('/')
def index():
    try:
        return redirect('login')
    except:
        return render_template('error.html', error=e)


@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        user_dao = UserDAO()
        user_vo = UserVO()
        if request.method == 'GET':
            return render_template('login.html')
        else:
            username = request.form.get('username')
            password = request.form.get('password')
            user_vo.username = username
            user_vo.password = password
            user = user_dao.view_one_user(user_vo)
            if user:
                login_user(user, remember=True)
                return redirect('/dashboard')
            return render_template('login.html', credentials="Invalid  Credentials")
    except Exception as e:
        return render_template('error.html', error=e)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('main_page.html')


@app.route("/logout")
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash('Logout successful!', 'success')
    else:
        flash('You are not logged in', 'error')
    return redirect('login')
