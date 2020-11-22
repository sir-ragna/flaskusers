from app import app
from app.database import *
from flask import render_template, request, flash, redirect, url_for, session
from functools import wraps
from flask_login import login_required, login_user, logout_user, current_user

@app.route('/')
def homepage():    
    return render_template('home.html.j2')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        logout_user()
        if 'email' in request.form and 'password' in request.form:
            email = request.form['email']
            password = request.form['password']
            if check_password(email, password):
                flash("Authentication succeeded")
                user_id = get_user_id(email)
                user = load_user(user_id)
                login_user(user)
                return redirect(url_for('homepage'))
            else:
                flash("Failed to authenticate")
        
    return render_template('login.html.j2')

@app.route('/logout')
def logout():
    logout_user()
    flash("signed out")
    return redirect(url_for('homepage'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if 'email' in request.form and 'password' in request.form:
            email = request.form['email']
            password = request.form['password']
            try:
                create_user(email, password)
                flash(f"User '{email}' created")
                return redirect(url_for('homepage'))
            except Exception as ex:
                app.logger.error('Could not register: {}'.format(ex), exc_info=True)
                flash("Failed to register")
       
    return render_template('register.html.j2')

@app.route('/admin')
@login_required
def admin():
    return "Only signed in users can see this"

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        if 'nickname' in request.form:
            save_nickname(current_user.user_id, request.form['nickname'])
        elif 'verifyme' in request.form:
            generate_verification_link(current_user.user_id)
            flash("requested a verification link")
            # TODO sent email somehow
    app.login_manager._load_user() ## NEEDED to refresh the 'current_user' in the template
    return render_template('profile.html.j2')

@app.route('/activate/<string:activation_code>')
def activate_email(activation_code):
    try:
        if verify_user_email(activation_code):
            flash("User has been activated")
            return redirect(url_for("homepage"))
    except Exception as ex:
        print("{}".format(ex))
    
    flash("Could not activate user")
    return redirect(url_for("homepage"))
    